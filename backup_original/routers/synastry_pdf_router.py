from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from kerykeion import AstrologicalSubject
from app.models import SynastryRequest
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
from typing import List, Dict
from pydantic import BaseModel, Field
import tempfile
import os
from pathlib import Path
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/api/v1",
    tags=["Synastry PDF"],
    dependencies=[Depends(verify_api_key)]
)

# Modelo para resposta de PDF
class SynastryPDFResponse(BaseModel):
    pdf_url: str = Field(..., description="URL do relatório PDF gerado")

def calculate_synastry_detailed(person1_data, person2_data) -> Dict:
    """Calcula sinastria detalhada para relatório PDF."""
    try:
        # Criar subjects para ambas as pessoas
        subject1 = create_subject(person1_data, person1_data.get('name', 'Person 1'))
        subject2 = create_subject(person2_data, person2_data.get('name', 'Person 2'))

        # Planetas principais para análise
        main_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

        # Obter posições dos planetas
        person1_planets = {}
        person2_planets = {}

        for planet in main_planets:
            if hasattr(subject1, planet):
                p1_obj = getattr(subject1, planet)
                if p1_obj and hasattr(p1_obj, 'position'):
                    person1_planets[planet] = {
                        'name': p1_obj.name,
                        'position': p1_obj.position,
                        'sign': p1_obj.sign,
                        'house': p1_obj.house_name.split('_')[0] if '_' in p1_obj.house_name else '1'
                    }

            if hasattr(subject2, planet):
                p2_obj = getattr(subject2, planet)
                if p2_obj and hasattr(p2_obj, 'position'):
                    person2_planets[planet] = {
                        'name': p2_obj.name,
                        'position': p2_obj.position,
                        'sign': p2_obj.sign,
                        'house': p2_obj.house_name.split('_')[0] if '_' in p2_obj.house_name else '1'
                    }

        # Calcular aspectos detalhados
        aspects = []
        compatibility_score = 0
        total_weight = 0

        for p1_key, p1_data in person1_planets.items():
            for p2_key, p2_data in person2_planets.items():
                angle = abs(p1_data['position'] - p2_data['position'])
                if angle > 180:
                    angle = 360 - angle

                # Verificar aspectos
                aspect_info = get_aspect_info(angle)
                if aspect_info:
                    aspect_name, aspect_type, orb = aspect_info

                    # Calcular peso do aspecto
                    planet_weights = {
                        'Sun': 3.0, 'Moon': 3.0, 'Mercury': 2.0, 'Venus': 2.5, 'Mars': 2.5,
                        'Jupiter': 1.5, 'Saturn': 1.5, 'Uranus': 1.0, 'Neptune': 1.0, 'Pluto': 1.0
                    }

                    p1_weight = planet_weights.get(p1_data['name'], 1.0)
                    p2_weight = planet_weights.get(p2_data['name'], 1.0)
                    avg_weight = (p1_weight + p2_weight) / 2

                    # Calcular score do aspecto
                    aspect_weights = {"harmonic": 1.0, "neutral": 0.5, "tense": -0.3}
                    aspect_score = aspect_weights.get(aspect_type, 0.0) * avg_weight

                    compatibility_score += aspect_score
                    total_weight += avg_weight

                    aspects.append({
                        'p1_planet': p1_data['name'],
                        'p1_sign': p1_data['sign'],
                        'p1_house': p1_data['house'],
                        'p2_planet': p2_data['name'],
                        'p2_sign': p2_data['sign'],
                        'p2_house': p2_data['house'],
                        'aspect_name': aspect_name,
                        'aspect_type': aspect_type,
                        'orb': round(orb, 2),
                        'interpretation': get_aspect_interpretation(p1_data['name'], p2_data['name'], aspect_name)
                    })

        # Normalizar score
        if total_weight > 0:
            compatibility_score = (compatibility_score / total_weight) * 50 + 50
        else:
            compatibility_score = 50

        compatibility_score = max(0, min(100, compatibility_score))

        return {
            'person1': person1_data,
            'person2': person2_data,
            'person1_planets': person1_planets,
            'person2_planets': person2_planets,
            'aspects': aspects,
            'compatibility_score': round(compatibility_score, 1),
            'summary': generate_detailed_summary(compatibility_score, aspects)
        }

    except Exception as e:
        print(f"Erro no cálculo detalhado de sinastria: {e}")
        return None

def get_aspect_info(angle: float, orb_tolerance: float = 8.0) -> tuple:
    """Determina informações do aspecto."""
    aspects = {
        0: ("conjunction", "harmonic"),
        30: ("semi_sextile", "neutral"),
        45: ("semi_square", "tense"),
        60: ("sextile", "harmonic"),
        90: ("square", "tense"),
        120: ("trine", "harmonic"),
        135: ("sesquiquadrate", "tense"),
        150: ("quincunx", "neutral"),
        180: ("opposition", "tense")
    }

    for aspect_angle, (name, type_) in aspects.items():
        if abs(angle - aspect_angle) <= orb_tolerance:
            return name, type_, abs(angle - aspect_angle)

    return None

def get_aspect_interpretation(p1: str, p2: str, aspect: str) -> str:
    """Gera interpretação básica do aspecto."""
    interpretations = {
        "conjunction": f"{p1} e {p2} em conjunção: energias se fundem e se intensificam mutuamente.",
        "sextile": f"{p1} em sextil com {p2}: harmonia e oportunidades de crescimento conjunto.",
        "square": f"{p1} em quadratura com {p2}: tensão criativa que pode gerar crescimento através de desafios.",
        "trine": f"{p1} em trígono com {p2}: fluxo natural e harmônico de energias.",
        "opposition": f"{p1} em oposição a {p2}: polaridades que se complementam quando equilibradas.",
        "semi_sextile": f"{p1} em semi-sextil com {p2}: conexão sutil que requer consciência.",
        "semi_square": f"{p1} em semi-quadratura com {p2}: irritação menor que pode ser trabalhada.",
        "sesquiquadrate": f"{p1} em sesquiquadratura com {p2}: tensão que requer ajustes.",
        "quincunx": f"{p1} em quincúncio com {p2}: necessidade de adaptação e flexibilidade."
    }

    return interpretations.get(aspect, f"{p1} e {p2}: aspecto especial que requer análise individual.")

def generate_detailed_summary(score: float, aspects: List[Dict]) -> str:
    """Gera resumo detalhado da compatibilidade."""
    harmonic_count = len([a for a in aspects if a['aspect_type'] == "harmonic"])
    tense_count = len([a for a in aspects if a['aspect_type'] == "tense"])
    neutral_count = len([a for a in aspects if a['aspect_type'] == "neutral"])

    if score >= 80:
        level = "excelente"
        description = "Vocês têm uma conexão natural muito forte e harmoniosa."
    elif score >= 65:
        level = "boa"
        description = "Há uma base sólida para um relacionamento duradouro e satisfatório."
    elif score >= 50:
        level = "moderada"
        description = "O relacionamento tem potencial, mas requer trabalho e compreensão mútua."
    elif score >= 35:
        level = "desafiadora"
        description = "Existem desafios significativos que podem ser superados com dedicação."
    else:
        level = "difícil"
        description = "O relacionamento requer muito trabalho e paciência de ambas as partes."

    summary = f"Compatibilidade {level} ({score:.1f}%). {description}\n\n"
    summary += f"Análise dos aspectos encontrados:\n"
    summary += f"• {harmonic_count} aspectos harmônicos (facilitam o relacionamento)\n"
    summary += f"• {tense_count} aspectos tensos (geram desafios e crescimento)\n"
    summary += f"• {neutral_count} aspectos neutros (requerem consciência)\n\n"

    if harmonic_count > tense_count:
        summary += "O relacionamento tem uma base predominantemente harmônica, com fluxo natural de energias."
    elif tense_count > harmonic_count:
        summary += "Os desafios presentes podem gerar muito crescimento se trabalhados com consciência."
    else:
        summary += "Há um equilíbrio entre harmonia e desafios, criando um relacionamento dinâmico."

    return summary

def generate_synastry_pdf(synastry_data: Dict) -> str:
    """Gera PDF da sinastria e retorna URL."""
    try:
        # Criar arquivo temporário para o markdown
        temp_dir = Path("/tmp/synastry_pdfs")
        temp_dir.mkdir(exist_ok=True)

        # Gerar ID único para o arquivo
        file_id = str(uuid.uuid4())
        md_file = temp_dir / f"synastry_{file_id}.md"
        pdf_file = temp_dir / f"synastry_{file_id}.pdf"

        # Gerar conteúdo markdown
        md_content = f"""# Relatório de Sinastria

## Dados das Pessoas

### {synastry_data['person1'].get('name', 'Pessoa 1')}
- **Data de Nascimento:** {synastry_data['person1']['day']}/{synastry_data['person1']['month']}/{synastry_data['person1']['year']}
- **Hora:** {synastry_data['person1']['hour']:02d}:{synastry_data['person1']['minute']:02d}
- **Local:** {synastry_data['person1']['latitude']:.4f}, {synastry_data['person1']['longitude']:.4f}

### {synastry_data['person2'].get('name', 'Pessoa 2')}
- **Data de Nascimento:** {synastry_data['person2']['day']}/{synastry_data['person2']['month']}/{synastry_data['person2']['year']}
- **Hora:** {synastry_data['person2']['hour']:02d}:{synastry_data['person2']['minute']:02d}
- **Local:** {synastry_data['person2']['latitude']:.4f}, {synastry_data['person2']['longitude']:.4f}

## Análise de Compatibilidade

### Score: {synastry_data['compatibility_score']}%

{synastry_data['summary']}

## Aspectos Detalhados

"""

        for aspect in synastry_data['aspects']:
            md_content += f"""### {aspect['p1_planet']} {aspect['aspect_name']} {aspect['p2_planet']}
- **Orbe:** {aspect['orb']}°
- **Tipo:** {aspect['aspect_type']}
- **Interpretação:** {aspect['interpretation']}

"""

        md_content += f"""
## Posições Planetárias

### {synastry_data['person1'].get('name', 'Pessoa 1')}
"""

        for planet, data in synastry_data['person1_planets'].items():
            md_content += f"- **{data['name']}:** {data['sign']} (Casa {data['house']})\n"

        md_content += f"""
### {synastry_data['person2'].get('name', 'Pessoa 2')}
"""

        for planet, data in synastry_data['person2_planets'].items():
            md_content += f"- **{data['name']}:** {data['sign']} (Casa {data['house']})\n"

        md_content += f"""

---
*Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*
*API ToAMAO - Astrologia Profissional*
"""

        # Escrever arquivo markdown
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # Converter para PDF usando o utilitário manus
        import subprocess
        result = subprocess.run([
            'manus-md-to-pdf', str(md_file), str(pdf_file)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Erro na conversão PDF: {result.stderr}")
            return None

        # Retornar URL do PDF (simulada - em produção seria um URL real)
        pdf_url = f"https://toamao-production.up.railway.app/static/pdfs/synastry_{file_id}.pdf"

        return pdf_url

    except Exception as e:
        print(f"Erro na geração do PDF: {e}")
        return None

@router.post("/synastry-pdf-report", response_model=SynastryPDFResponse)
async def generate_synastry_pdf_report(request: SynastryRequest):
    """
    Gera relatório completo de sinastria em PDF.
    Mesma lógica da sinastria, mas retorna link para relatório em PDF.
    """
    try:
        # Converter request para dicionários
        person1_data = request.person1.dict()
        person2_data = request.person2.dict()

        # Calcular sinastria detalhada
        synastry_data = calculate_synastry_detailed(person1_data, person2_data)

        if not synastry_data:
            raise HTTPException(status_code=400, detail="Erro no cálculo da sinastria")

        # Gerar PDF
        pdf_url = generate_synastry_pdf(synastry_data)

        if not pdf_url:
            raise HTTPException(status_code=500, detail="Erro na geração do PDF")

        return SynastryPDFResponse(pdf_url=pdf_url)

    except Exception as e:
        print(f"Erro no endpoint de sinastria PDF: {e}")
        raise HTTPException(status_code=400, detail=f"Erro na geração do relatório PDF: {str(e)}")
