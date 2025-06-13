from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.models import TransitRequest
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import math

router = APIRouter(
    prefix="/api/v1",
    tags=["Daily & Weekly Transits"],
    dependencies=[Depends(verify_api_key)]
)

# Modelos específicos para trânsitos diários e semanais
class DailyTransitRequest(BaseModel):
    year: int = Field(..., description="Ano")
    month: int = Field(..., description="Mês (1-12)")
    day: int = Field(..., description="Dia")

class TransitAspectDaily(BaseModel):
    p1: str = Field(..., description="Primeiro planeta")
    p2: str = Field(..., description="Segundo planeta")
    type: str = Field(..., description="Tipo do aspecto (sextile, square, etc)")
    orb: float = Field(..., description="Orbe do aspecto")

class DailyTransitsResponse(BaseModel):
    aspects: List[TransitAspectDaily]

class WeeklyDay(BaseModel):
    date: str
    aspects: List[TransitAspectDaily]
    summary: str

class WeeklyTransitsResponse(BaseModel):
    days: List[WeeklyDay]

def calculate_aspect_angle(pos1: float, pos2: float) -> float:
    """Calcula o ângulo entre duas posições planetárias."""
    diff = abs(pos1 - pos2)
    if diff > 180:
        diff = 360 - diff
    return diff

def get_aspect_name_simple(angle: float, orb_tolerance: float = 8.0) -> tuple:
    """Determina o nome do aspecto baseado no ângulo."""
    aspects = {
        0: "conjunction",
        30: "semi_sextile",
        45: "semi_square",
        60: "sextile",
        90: "square",
        120: "trine",
        135: "sesquiquadrate",
        150: "quincunx",
        180: "opposition"
    }

    for aspect_angle, name in aspects.items():
        if abs(angle - aspect_angle) <= orb_tolerance:
            return name, abs(angle - aspect_angle)

    return None, None

def calculate_daily_aspects(year: int, month: int, day: int) -> List[TransitAspectDaily]:
    """Calcula aspectos planetários para um dia específico."""
    try:
        # Criar subject para o dia específico (meio-dia GMT)
        subject = AstrologicalSubject(
            name=f"Transits_{year}_{month}_{day}",
            year=year, month=month, day=day,
            hour=12, minute=0,
            lat=0.0, lng=0.0,  # GMT
            tz_str="UTC"
        )

        # Planetas principais para análise
        main_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']

        # Obter posições dos planetas
        planet_positions = {}
        for planet in main_planets:
            if hasattr(subject, planet):
                p_obj = getattr(subject, planet)
                if p_obj and hasattr(p_obj, 'position'):
                    planet_positions[planet] = {
                        'name': p_obj.name,
                        'position': p_obj.position
                    }

        # Calcular aspectos entre planetas
        aspects = []
        planet_keys = list(planet_positions.keys())

        for i, p1_key in enumerate(planet_keys):
            for p2_key in planet_keys[i+1:]:
                p1_data = planet_positions[p1_key]
                p2_data = planet_positions[p2_key]

                angle = calculate_aspect_angle(p1_data['position'], p2_data['position'])
                aspect_name, orb = get_aspect_name_simple(angle)

                if aspect_name and orb is not None and orb <= 5.0:  # Orbe mais apertado para trânsitos diários
                    aspects.append(TransitAspectDaily(
                        p1=p1_data['name'],
                        p2=p2_data['name'],
                        type=aspect_name,
                        orb=round(orb, 2)
                    ))

        return aspects

    except Exception as e:
        print(f"Erro no cálculo de aspectos diários: {e}")
        return []

@router.post("/transits/daily", response_model=DailyTransitsResponse)
async def get_daily_transits(request: DailyTransitRequest):
    """
    Retorna todos os aspectos planetários ativos para um dia específico.
    Lista trânsitos do dia (GMT-0).
    """
    try:
        aspects = calculate_daily_aspects(request.year, request.month, request.day)

        return DailyTransitsResponse(aspects=aspects)

    except Exception as e:
        print(f"Erro no endpoint de trânsitos diários: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo de trânsitos diários: {str(e)}")

@router.post("/transits/weekly", response_model=WeeklyTransitsResponse)
async def get_weekly_transits(request: DailyTransitRequest):
    """
    Entrega predição de 7 dias resumida (bom para alertas semanais).
    Calcula aspectos para os próximos 7 dias a partir da data fornecida.
    """
    try:
        weekly_data = []
        base_date = datetime(request.year, request.month, request.day)

        for i in range(7):
            current_date = base_date + timedelta(days=i)
            aspects = calculate_daily_aspects(current_date.year, current_date.month, current_date.day)

            # Gerar resumo do dia
            if not aspects:
                summary = "Dia tranquilo, sem aspectos planetários significativos."
            else:
                harmonic_count = len([a for a in aspects if a.type in ["sextile", "trine", "conjunction"]])
                tense_count = len([a for a in aspects if a.type in ["square", "opposition", "semi_square", "sesquiquadrate"]])

                if harmonic_count > tense_count:
                    summary = f"Dia harmonioso com {len(aspects)} aspectos, predominando energias positivas."
                elif tense_count > harmonic_count:
                    summary = f"Dia desafiador com {len(aspects)} aspectos, requer atenção e paciência."
                else:
                    summary = f"Dia equilibrado com {len(aspects)} aspectos mistos."

            weekly_data.append(WeeklyDay(
                date=current_date.strftime("%Y-%m-%d"),
                aspects=aspects,
                summary=summary
            ))

        return WeeklyTransitsResponse(days=weekly_data)

    except Exception as e:
        print(f"Erro no endpoint de trânsitos semanais: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo de trânsitos semanais: {str(e)}")
