from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from app.models import SVGChartRequest, NatalChartRequest, TransitRequest
from kerykeion.charts.kerykeion_chart_svg import KerykeionChartSVG
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
import base64
import os
import glob
from pathlib import Path
from typing import Dict, Literal

router = APIRouter(prefix="/api/v1", tags=["svg_charts"], dependencies=[Depends(verify_api_key)])

@router.post("/svg_chart",
             response_class=Response,
             responses={
                 200: {
                     "content": {"image/svg+xml": {}},
                     "description": "Retorna o gráfico SVG diretamente."
                 },
                 422: {"description": "Erro de validação nos dados de entrada."},
                 500: {"description": "Erro interno ao gerar o gráfico."}
             })
async def generate_svg_chart(data: SVGChartRequest):
    """Gera um gráfico SVG para um mapa natal, trânsito ou combinação."""
    try:
        natal_subject = create_subject(data.natal_chart, "Natal Chart")

        transit_subject = None
        if data.transit_chart and (data.chart_type == "transit" or data.chart_type == "combined"):
            transit_subject = create_subject(data.transit_chart, "Transit")

        # Mapear o tipo de gráfico para o formato esperado pelo KerykeionChartSVG
        chart_type_map = {
            "natal": "Natal",
            "transit": "Transit",
            "combined": "Synastry"
        }

        # Criar um diretório temporário para salvar o SVG
        temp_dir = Path("/tmp/astro_svg")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Limpar arquivos SVG anteriores para evitar confusão
        for old_file in temp_dir.glob("*.svg"):
            try:
                old_file.unlink()
            except:
                pass

        # Nome do arquivo temporário
        chart_name = data.natal_chart.name or "chart"

        # Gerar o gráfico SVG com base no tipo
        if data.chart_type == "natal":
            chart = KerykeionChartSVG(natal_subject, chart_type=chart_type_map[data.chart_type])
        elif data.chart_type == "transit" and transit_subject:
            chart = KerykeionChartSVG(transit_subject, chart_type=chart_type_map[data.chart_type])
        elif data.chart_type == "combined" and transit_subject:
            # Kerykeion usa 'Synastry' para gráficos combinados natal+trânsito
            chart = KerykeionChartSVG(natal_subject, chart_type=chart_type_map[data.chart_type], second_subject=transit_subject)
        else:
            # Caso onde transit_chart é necessário mas não fornecido
            if data.chart_type in ["transit", "combined"] and not transit_subject:
                 raise ValueError(f"Dados de trânsito ('transit_chart') são necessários para o tipo de gráfico '{data.chart_type}'.")
            raise ValueError("Configuração de tipo de gráfico inválida ou dados ausentes.")

        # Configurar tema (usando método disponível na versão atual)
        try:
            chart.set_up_theme(data.theme)
        except Exception as theme_err:
             print(f"Aviso: Não foi possível aplicar o tema '{data.theme}': {theme_err}")

        # Configurar o diretório de saída para o SVG - usando Path
        chart.output_directory = temp_dir

        # Gerar o SVG - este método salva o arquivo em disco
        chart.makeSVG()

        # Encontrar o arquivo SVG gerado mais recente no diretório
        svg_files = list(temp_dir.glob("*.svg"))
        if not svg_files:
            raise FileNotFoundError("Nenhum arquivo SVG foi gerado")

        # Ordenar por data de modificação (mais recente primeiro)
        svg_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        svg_file_path = svg_files[0]

        # Ler o conteúdo do arquivo SVG gerado
        with open(svg_file_path, 'r') as svg_file:
            svg_content = svg_file.read()

        # Remover o arquivo temporário após leitura
        try:
            os.remove(svg_file_path)
        except:
            pass  # Ignorar erros na remoção do arquivo temporário

        # Retornar o SVG como resposta
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"inline; filename=chart_{chart_name}.svg"} # Usar inline para visualização
        )
    except ValueError as ve:
         raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Logar o erro real no servidor para depuração
        print(f"Erro detalhado ao gerar SVG: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico SVG: {type(e).__name__}")

@router.post("/svg_chart_base64",
             response_model=Dict[str, str],
             summary="Gera gráfico SVG em Base64",
             description="Gera um gráfico SVG e retorna como string base64, útil para incorporação em aplicações web.")
async def generate_svg_chart_base64(data: SVGChartRequest):
    """
    Gera um gráfico SVG e retorna como string base64.
    """
    try:
        # Reutilizar a lógica do endpoint anterior para obter a Response SVG
        svg_response = await generate_svg_chart(data)

        # Verificar se a resposta foi bem-sucedida antes de acessar o body
        if svg_response.status_code != 200:
             # Se generate_svg_chart levantou HTTPException, ela será propagada
             # Este check é uma segurança adicional
             raise HTTPException(status_code=svg_response.status_code, detail="Falha ao gerar SVG base.")

        svg_content_bytes = svg_response.body

        # Converter para base64
        base64_svg = base64.b64encode(svg_content_bytes).decode("utf-8")

        # Retornar como JSON
        return {
            "svg_base64": base64_svg,
            "data_uri": f"data:image/svg+xml;base64,{base64_svg}"
        }
    # Capturar exceções específicas ou genéricas que podem ocorrer
    except HTTPException as http_exc:
        # Re-levantar HTTPExceptions para manter o status code e detalhes originais
        raise http_exc
    except Exception as e:
        # Logar o erro real no servidor para depuração
        print(f"Erro detalhado ao gerar SVG base64: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico SVG em base64: {type(e).__name__}")
