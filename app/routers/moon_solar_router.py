from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, get_house_from_kerykeion_attribute
from app.models import NatalChartRequest
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import math

router = APIRouter(
    prefix="/api/v1",
    tags=["Moon Phase & Solar Return"],
    dependencies=[Depends(verify_api_key)]
)

# Modelos para fases da lua
class MoonPhaseRequest(BaseModel):
    year: int = Field(..., description="Ano")
    month: int = Field(..., description="Mês (1-12)")
    day: int = Field(..., description="Dia")

class MoonPhaseResponse(BaseModel):
    phase: str = Field(..., description="Fase da lua")
    illumination: float = Field(..., description="Percentual de iluminação (0-100)")

# Modelos para retorno solar
class SolarReturnRequest(BaseModel):
    year: int = Field(..., description="Ano de nascimento")
    month: int = Field(..., description="Mês de nascimento")
    day: int = Field(..., description="Dia de nascimento")
    hour: int = Field(..., description="Hora de nascimento")
    minute: int = Field(..., description="Minuto de nascimento")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    tz_str: str = Field(..., description="Timezone")

class SolarReturnResponse(BaseModel):
    date: str = Field(..., description="Data do retorno solar")
    highlights: List[str] = Field(..., description="Destaques do retorno solar")

def calculate_moon_phase(year: int, month: int, day: int) -> tuple:
    """
    Calcula a fase da lua para uma data específica.
    Baseado no algoritmo de cálculo de fases lunares.
    """
    try:
        # Criar subject para obter posição da lua
        subject = AstrologicalSubject(
            name=f"Moon_{year}_{month}_{day}",
            year=year, month=month, day=day,
            hour=12, minute=0,
            lat=0.0, lng=0.0,
            tz_str="UTC"
        )

        if not hasattr(subject, 'moon') or not subject.moon:
            return "unknown", 0.0

        moon_pos = subject.moon.position
        sun_pos = subject.sun.position

        # Calcular diferença angular entre Sol e Lua
        diff = moon_pos - sun_pos
        if diff < 0:
            diff += 360

        # Calcular iluminação baseada na diferença angular
        # 0° = Lua Nova (0%), 180° = Lua Cheia (100%)
        illumination = (1 - math.cos(math.radians(diff))) / 2 * 100

        # Determinar fase baseada na diferença angular
        if diff < 45 or diff >= 315:
            phase = "Nova"
        elif 45 <= diff < 135:
            phase = "Crescente"
        elif 135 <= diff < 225:
            phase = "Cheia"
        else:
            phase = "Minguante"

        return phase, round(illumination, 1)

    except Exception as e:
        print(f"Erro no cálculo da fase da lua: {e}")
        return "unknown", 0.0

def calculate_solar_return(birth_year: int, birth_month: int, birth_day: int,
                          birth_hour: int, birth_minute: int,
                          lat: float, lng: float, tz_str: str) -> tuple:
    """
    Calcula a data do próximo retorno solar e gera destaques.
    """
    try:
        # Criar subject natal para obter posição do Sol
        natal_data = NatalChartRequest(
            year=birth_year,
            month=birth_month,
            day=birth_day,
            hour=birth_hour,
            minute=birth_minute,
            latitude=lat,
            longitude=lng,
            tz_str=tz_str,
        )
        natal_subject = create_subject(natal_data, "Natal")

        natal_sun_pos = natal_subject.sun.position

        # Calcular próximo aniversário
        current_year = datetime.now().year
        next_birthday = datetime(current_year, birth_month, birth_day)

        if next_birthday < datetime.now():
            next_birthday = datetime(current_year + 1, birth_month, birth_day)

        # Criar subject para o retorno solar (aproximado)
        sr_data = NatalChartRequest(
            year=next_birthday.year,
            month=next_birthday.month,
            day=next_birthday.day,
            hour=birth_hour,
            minute=birth_minute,
            latitude=lat,
            longitude=lng,
            tz_str=tz_str,
        )
        sr_subject = create_subject(sr_data, "Solar Return")

        # Gerar destaques baseados nas posições planetárias
        highlights = []

        # Analisar posição da Lua no retorno solar
        moon_sign = sr_subject.moon.sign if hasattr(sr_subject, 'moon') else "unknown"
        highlights.append(f"Lua em {moon_sign} - foco nas emoções e intuição")

        # Analisar Ascendente
        asc_sign = sr_subject.first_house.sign if hasattr(sr_subject, 'first_house') else "unknown"
        highlights.append(f"Ascendente em {asc_sign} - nova identidade e abordagem")

        # Analisar planetas em destaque
        if hasattr(sr_subject, 'mars'):
            mars_house = get_house_from_kerykeion_attribute(sr_subject.mars)
            highlights.append(f"Marte na casa {mars_house} - área de ação e energia")

        if hasattr(sr_subject, 'venus'):
            venus_sign = sr_subject.venus.sign
            highlights.append(f"Vênus em {venus_sign} - relacionamentos e valores")

        # Adicionar previsão geral
        highlights.append("Ano de renovação e novos ciclos pessoais")

        return next_birthday.strftime("%Y-%m-%dT%H:%M:%SZ"), highlights

    except Exception as e:
        print(f"Erro no cálculo do retorno solar: {e}")
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), ["Erro no cálculo"]

@router.post("/moon_phase", response_model=MoonPhaseResponse)
async def get_moon_phase(request: MoonPhaseRequest):
    """
    Informa a fase da Lua para uma data específica.
    Ótimo para push "Lua Cheia hoje!".
    """
    try:
        phase, illumination = calculate_moon_phase(request.year, request.month, request.day)

        return MoonPhaseResponse(
            phase=phase,
            illumination=illumination
        )

    except Exception as e:
        print(f"Erro no endpoint de fase da lua: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo da fase da lua: {str(e)}")

@router.post("/solar_return", response_model=SolarReturnResponse)
async def get_solar_return(request: SolarReturnRequest):
    """
    Calcula o próximo retorno solar e fornece destaques astrológicos.
    Retorna a data exata do aniversário solar e principais influências.
    """
    try:
        date, highlights = calculate_solar_return(
            request.year, request.month, request.day,
            request.hour, request.minute,
            request.latitude, request.longitude, request.tz_str
        )

        return SolarReturnResponse(
            date=date,
            highlights=highlights
        )

    except Exception as e:
        print(f"Erro no endpoint de retorno solar: {e}")
        raise HTTPException(status_code=400, detail=f"Erro no cálculo do retorno solar: {str(e)}")
