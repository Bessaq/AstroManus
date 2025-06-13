from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from app.models import SVGCombinedChartRequest
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
from app.utils.svg_combined_chart import generate_combined_chart
from pathlib import Path
import base64
import os
import re
from typing import Dict

router = APIRouter(prefix="/api/v1", tags=["svg_charts"], dependencies=[Depends(verify_api_key)])

# Função para sanitizar nomes de arquivos
def sanitize_filename(filename):
    # Remover caracteres especiais e espaços
    sanitized = re.sub(r'[^\w\-_]', '_', filename)
    return sanitized

@router.post("/svg_combined_chart",
             response_class=Response,
             responses={
                 200: {
                     "content": {"image/svg+xml": {}},
                     "description": "Retorna o gráfico SVG combinado diretamente."
                 },
                 422: {"description": "Erro de validação nos dados de entrada."},
                 500: {"description": "Erro interno ao gerar o gráfico."}
             })
async def generate_svg_combined_chart(data: SVGCombinedChartRequest):
    """
    Gera um gráfico SVG combinado mostrando o mapa natal e os trânsitos com aspectos entre eles.

    Este endpoint cria uma visualização que mostra tanto os planetas do mapa natal quanto
    os planetas em trânsito, com linhas coloridas representando os aspectos entre eles.
    """
    try:
        # Criar os objetos astrológicos
        natal_subject = create_subject(data.natal_chart, data.natal_chart.name or "Natal Chart")
        transit_subject = create_subject(data.transit_chart, data.transit_chart.name or "Transit Chart")

        # Criar um diretório temporário para salvar o SVG
        temp_dir = Path("/tmp/astro_svg")
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Limpar arquivos SVG anteriores para evitar confusão
        for old_file in temp_dir.glob("*.svg"):
            try:
                old_file.unlink()
            except:
                pass

        # Gerar o SVG combinado
        svg_path = generate_combined_chart(natal_subject, transit_subject, temp_dir)

        # Retornar o SVG como resposta
        return FileResponse(
            path=svg_path,
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"inline; filename=combined_chart.svg"}
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Logar o erro real no servidor para depuração
        print(f"Erro detalhado ao gerar SVG combinado: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico SVG combinado: {type(e).__name__}")

@router.post("/svg_combined_chart_base64",
             response_model=Dict[str, str],
             summary="Gera gráfico SVG combinado em Base64",
             description="Gera um gráfico SVG combinado de mapa natal e trânsitos e retorna como string base64, útil para incorporação em aplicações web.")
async def generate_svg_combined_chart_base64(data: SVGCombinedChartRequest):
    """
    Gera um gráfico SVG combinado e retorna como string base64.
    """
    try:
        # Reutilizar a lógica do endpoint anterior para obter a Response SVG
        svg_response = await generate_svg_combined_chart(data)

        # Verificar se a resposta foi bem-sucedida
        if not isinstance(svg_response, FileResponse):
            raise HTTPException(status_code=500, detail="Falha ao gerar SVG base.")

        # Ler o conteúdo do arquivo SVG
        with open(svg_response.path, 'rb') as f:
            svg_content = f.read()

        # Converter para base64
        base64_svg = base64.b64encode(svg_content).decode("utf-8")

        # Retornar como JSON
        return {
            "svg_base64": base64_svg,
            "data_uri": f"data:image/svg+xml;base64,{base64_svg}"
        }
    except HTTPException as http_exc:
        # Re-levantar HTTPExceptions para manter o status code e detalhes originais
        raise http_exc
    except Exception as e:
        # Logar o erro real no servidor para depuração
        print(f"Erro detalhado ao gerar SVG base64 combinado: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico SVG combinado em base64: {type(e).__name__}")
