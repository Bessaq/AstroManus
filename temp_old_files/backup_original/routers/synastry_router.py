from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.models import SynastryRequest, SynastryResponse, SynastryAspect
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
from typing import List, Dict
import math

router = APIRouter(
    prefix="/api/v1",
    tags=["Synastry"],
    dependencies=[Depends(verify_api_key)]
)

def calculate_aspect_angle(pos1: float, pos2: float) -> float:
    """Calcula o ângulo entre duas posições planetárias."""
    diff = abs(pos1 - pos2)
    if diff > 180:
        diff = 360 - diff
    return diff

def get_aspect_name(angle: float, orb_tolerance: float = 8.0) -> tuple:
    """Determina o nome do aspecto baseado no ângulo."""
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

    return None, None, None

def calculate_compatibility_score(aspects: List[SynastryAspect]) -> float:
    """Calcula um score de compatibilidade baseado nos aspectos."""
    if not aspects:
        return 0.0

    score = 0.0
    total_weight = 0.0

    # Pesos por tipo de aspecto
    aspect_weights = {
        "harmonic": 1.0,
        "neutral": 0.5,
        "tense": -0.3
    }

    # Pesos por planetas (planetas pessoais têm mais peso)
    planet_weights = {
        "Sun": 3.0, "Moon": 3.0, "Mercury": 2.0, "Venus": 2.5, "Mars": 2.5,
        "Jupiter": 1.5, "Saturn": 1.5, "Uranus": 1.0, "Neptune": 1.0, "Pluto": 1.0
    }

    for aspect in aspects:
        aspect_weight = aspect_weights.get(aspect.aspect_type, 0.0)
        p1_weight = planet_weights.get(aspect.p1_planet, 1.0)
        p2_weight = planet_weights.get(aspect.p2_planet, 1.0)

        # Orb mais apertado = aspecto mais forte
        orb_factor = max(0.1, (8.0 - aspect.orb) / 8.0)

        planet_avg_weight = (p1_weight + p2_weight) / 2
        aspect_score = aspect_weight * planet_avg_weight * orb_factor

        score += aspect_score
        total_weight += planet_avg_weight * orb_factor

    if total_weight == 0:
        return 0.0

    # Normalizar para 0-100
    normalized_score = (score / total_weight) * 50 + 50
    return max(0.0, min(100.0, normalized_score))

def generate_compatibility_summary(score: float, aspects: List[SynastryAspect]) -> str:
    """Gera um resumo textual da compatibilidade."""
    harmonic_count = len([a for a in aspects if a.aspect_type == "harmonic"])
    tense_count = len([a for a in aspects if a.aspect_type == "tense"])
    neutral_count = len([a for a in aspects if a.aspect_type == "neutral"])

    if score >= 80:
        level = "excelente"
    elif score >= 65:
        level = "boa"
    elif score >= 50:
        level = "moderada"
    elif score >= 35:
        level = "desafiadora"
    else:
        level = "difícil"

    summary = f"Compatibilidade {level} ({score:.1f}%). "
    summary += f"Encontrados {len(aspects)} aspectos: "
    summary += f"{harmonic_count} harmônicos, {tense_count} tensos, {neutral_count} neutros."

    if harmonic_count > tense_count:
        summary += " Relacionamento com boa base harmônica."
    elif tense_count > harmonic_count:
        summary += " Relacionamento com desafios que podem gerar crescimento."
    else:
        summary += " Relacionamento equilibrado entre harmonia e desafios."

    return summary

@router.post("/synastry", response_model=SynastryResponse)
async def calculate_synastry(request: SynastryRequest):
    """
    Calcula a sinastria (compatibilidade) entre dois mapas natais.
    Analisa os aspectos entre os planetas das duas pessoas.
    """
    try:
        # Criar subjects para ambas as pessoas
        subject1 = create_subject(request.person1, request.person1.name or "Person 1")
        subject2 = create_subject(request.person2, request.person2.name or "Person 2")

        # Planetas principais para análise de sinastria
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
                        'position': p1_obj.position
                    }

            if hasattr(subject2, planet):
                p2_obj = getattr(subject2, planet)
                if p2_obj and hasattr(p2_obj, 'position'):
                    person2_planets[planet] = {
                        'name': p2_obj.name,
                        'position': p2_obj.position
                    }

        # Calcular aspectos entre os planetas das duas pessoas
        aspects = []

        for p1_key, p1_data in person1_planets.items():
            for p2_key, p2_data in person2_planets.items():
                angle = calculate_aspect_angle(p1_data['position'], p2_data['position'])
                aspect_name, aspect_type, orb = get_aspect_name(angle)

                if aspect_name and orb is not None:
                    aspects.append(SynastryAspect(
                        p1_planet=p1_data['name'],
                        p2_planet=p2_data['name'],
                        aspect_name=aspect_name,
                        orb=round(orb, 2),
                        aspect_type=aspect_type
                    ))

        # Calcular score de compatibilidade
        compatibility_score = calculate_compatibility_score(aspects)

        # Gerar resumo
        summary = generate_compatibility_summary(compatibility_score, aspects)

        return SynastryResponse(
            person1_data=request.person1,
            person2_data=request.person2,
            aspects=aspects,
            compatibility_score=round(compatibility_score, 1),
            summary=summary
        )

    except Exception as e:
        print(f"Erro no cálculo de sinastria: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro no cálculo de sinastria: {str(e)}")
