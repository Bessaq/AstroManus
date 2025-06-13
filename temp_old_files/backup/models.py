from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum

# Modelos existentes (mantidos para referência)
class HouseSystem(str, Enum):
    PLACIDUS = "placidus"
    KOCH = "koch"
    REGIOMONTANUS = "regiomontanus"
    CAMPANUS = "campanus"
    EQUAL = "equal"
    WHOLE_SIGN = "whole_sign"

# Mapeamento de sistemas de casas para identificadores do Kerykeion
HOUSE_SYSTEM_MAP = {
    "placidus": "P",
    "koch": "K",
    "regiomontanus": "R",
    "campanus": "C",
    "equal": "E",
    "whole_sign": "W"
}

class PlanetPosition(BaseModel):
    name: str
    sign: str
    sign_num: int
    position: float
    abs_pos: float
    house_name: str
    speed: float = 0.0
    retrograde: bool = False

class NatalChartRequest(BaseModel):
    name: Optional[str] = Field(None, description="Nome da pessoa ou evento")
    year: int = Field(..., description="Ano de nascimento")
    month: int = Field(..., description="Mês de nascimento (1-12)")
    day: int = Field(..., description="Dia de nascimento (1-31)")
    hour: int = Field(..., description="Hora de nascimento (0-23)")
    minute: int = Field(..., description="Minuto de nascimento (0-59)")
    latitude: float = Field(..., description="Latitude do local de nascimento")
    longitude: float = Field(..., description="Longitude do local de nascimento")
    tz_str: str = Field(..., description="String de fuso horário (ex: 'America/Sao_Paulo')")
    house_system: HouseSystem = Field(HouseSystem.PLACIDUS, description="Sistema de casas a ser usado")

class TransitRequest(BaseModel):
    year: int = Field(..., description="Ano do trânsito")
    month: int = Field(..., description="Mês do trânsito (1-12)")
    day: int = Field(..., description="Dia do trânsito (1-31)")
    hour: int = Field(..., description="Hora do trânsito (0-23)")
    minute: int = Field(..., description="Minuto do trânsito (0-59)")
    latitude: float = Field(..., description="Latitude do local para cálculo do trânsito")
    longitude: float = Field(..., description="Longitude do local para cálculo do trânsito")
    tz_str: str = Field(..., description="String de fuso horário (ex: 'America/Sao_Paulo')")
    house_system: HouseSystem = Field(HouseSystem.PLACIDUS, description="Sistema de casas a ser usado")
    name: Optional[str] = Field(None, description="Nome opcional para o trânsito (ex: 'Trânsitos 2025')")

# Novo modelo para requisição de SVG combinado
class SVGCombinedChartRequest(BaseModel):
    """
    Modelo para requisição de gráfico SVG combinado de mapa natal e trânsitos.
    """
    natal_chart: NatalChartRequest = Field(..., description="Dados do mapa natal")
    transit_chart: TransitRequest = Field(..., description="Dados do trânsito")

    class Config:
        schema_extra = {
            "example": {
                "natal_chart": {
                    "name": "João",
                    "year": 1997,
                    "month": 10,
                    "day": 13,
                    "hour": 22,
                    "minute": 0,
                    "latitude": -3.7172,
                    "longitude": -38.5247,
                    "tz_str": "America/Fortaleza",
                    "house_system": "placidus"
                },
                "transit_chart": {
                    "name": "Trânsitos 2025",
                    "year": 2025,
                    "month": 6,
                    "day": 2,
                    "hour": 12,
                    "minute": 0,
                    "latitude": -3.7172,
                    "longitude": -38.5247,
                    "tz_str": "America/Fortaleza",
                    "house_system": "placidus"
                }
            }
        }

# -*- coding: utf-8 -*-
"""Modulo de rotas para calculo de mapa astral natal."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

from kerykeion import AstrologicalSubject
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP, HOUSE_NUMBER_TO_NAME_BASE

router = APIRouter(
    prefix="/api/v1",
    tags=["Natal Chart"],
    dependencies=[Depends(verify_api_key)]
)

# --- Enums e Modelos de Dados --- #

class HouseSystem(str, Enum):
    PLACIDUS = "placidus"
    KOCH = "koch"
    REGIOMONTANUS = "regiomontanus"
    CAMPANUS = "campanus"
    EQUAL = "equal"
    WHOLE_SIGN = "whole_sign"

class NatalChartRequest(BaseModel):
    name: Optional[str] = Field(None, description="Nome da pessoa ou evento")
    year: int = Field(..., description="Ano de nascimento")
    month: int = Field(..., description="Mês de nascimento (1-12)")
    day: int = Field(..., description="Dia de nascimento (1-31)")
    hour: int = Field(..., description="Hora de nascimento (0-23)")
    minute: int = Field(..., description="Minuto de nascimento (0-59)")
    latitude: float = Field(..., description="Latitude do local de nascimento")
    longitude: float = Field(..., description="Longitude do local de nascimento")
    tz_str: str = Field(..., description="String de fuso horário (ex: 'America/Sao_Paulo')")
    house_system: HouseSystem = Field(HouseSystem.PLACIDUS, description="Sistema de casas a ser usado")

class PlanetData(BaseModel):
    name: str
    name_original: str
    longitude: float
    latitude: float
    sign: str
    sign_original: str
    sign_num: int
    house: int
    retrograde: bool

class HouseCuspData(BaseModel):
    number: int
    sign: str
    sign_original: str
    sign_num: int
    longitude: float

class AspectData(BaseModel):
    p1_name: str
    p1_name_original: str
    p1_owner: str
    p2_name: str
    p2_name_original: str
    p2_owner: str
    aspect: str
    aspect_original: str
    orbit: float
    aspect_degrees: float
    diff: float
    applying: bool

class NatalChartResponse(BaseModel):
    input_data: NatalChartRequest
    planets: Dict[str, PlanetData]
    houses: Dict[str, HouseCuspData]
    ascendant: HouseCuspData
    midheaven: HouseCuspData
    aspects: List[AspectData]
    house_system: HouseSystem
    interpretations: Optional[Dict[str, str]] = None # Placeholder para futuras interpretações

# --- Endpoint --- #

@router.post("/natal_chart", response_model=NatalChartResponse)
async def create_natal_chart(request: NatalChartRequest):
    try:
        subject = create_subject(request, request.name if request.name else "NatalChart")

        planets_dict: Dict[str, PlanetData] = {}
        for k_name, api_name in PLANETS_MAP.items():
            planet_data = get_planet_data(subject, k_name, api_name)
            if planet_data:
                planets_dict[k_name] = PlanetData(
                    name=planet_data.name,
                    name_original=planet_data.name,
                    longitude=planet_data.position,
                    latitude=0.0, # Valor padrão
                    sign=planet_data.sign,
                    sign_original=planet_data.sign,
                    sign_num=planet_data.sign_num,
                    house=int(planet_data.house_name.split("_")[0]) if "_" in planet_data.house_name else 1,
                    retrograde=planet_data.retrograde
                )

        if hasattr(subject, 'chiron') and subject.chiron:
            chiron_data = get_planet_data(subject, 'chiron', 'Chiron')
            if chiron_data:
                planets_dict['chiron'] = PlanetData(
                    name="Chiron", name_original="Chiron", longitude=chiron_data.position, latitude=0.0,
                    sign=chiron_data.sign, sign_original=chiron_data.sign, sign_num=chiron_data.sign_num,
                    house=int(chiron_data.house_name.split("_")[0]) if "_" in chiron_data.house_name else 1,
                    retrograde=chiron_data.retrograde
                )

        if hasattr(subject, 'lilith') and subject.lilith and subject.lilith.name:
            planets_dict['lilith'] = PlanetData(
                name="Lilith", name_original="Lilith", longitude=subject.lilith.position, latitude=0.0,
                sign=subject.lilith.sign, sign_original=subject.lilith.sign, sign_num=subject.lilith.sign_num,
                house=int(subject.lilith.house_name.split("_")[0]) if hasattr(subject.lilith, 'house_name') and "_" in subject.lilith.house_name else 1,
                retrograde=False
            )

        houses_dict: Dict[str, HouseCuspData] = {}
        for i in range(1, 13):
            house_name_base = HOUSE_NUMBER_TO_NAME_BASE.get(i)
            if not house_name_base: continue
            house_obj_attr_name = f"{house_name_base}_house"
            house_obj = getattr(subject, house_obj_attr_name)
            houses_dict[str(i)] = HouseCuspData(
                number=i, sign=house_obj.sign, sign_original=house_obj.sign,
                sign_num=getattr(house_obj, 'sign_num', 1), longitude=round(house_obj.position, 4)
            )

        ascendant = HouseCuspData(
            number=1, sign=subject.first_house.sign, sign_original=subject.first_house.sign,
            sign_num=getattr(subject.first_house, 'sign_num', 1), longitude=round(subject.first_house.position, 4)
        )
        midheaven = HouseCuspData(
            number=10, sign=subject.tenth_house.sign, sign_original=subject.tenth_house.sign,
            sign_num=getattr(subject.tenth_house, 'sign_num', 1), longitude=round(subject.tenth_house.position, 4)
        )

        aspects_list: List[AspectData] = []
        main_planets_for_aspects = [
            subject.sun, subject.moon, subject.mercury, subject.venus, subject.mars,
            subject.jupiter, subject.saturn, subject.uranus, subject.neptune, subject.pluto
        ]
        processed_aspects = set()
        for p1 in main_planets_for_aspects:
            if not p1 or not hasattr(p1, 'aspects'): continue
            for asp in p1.aspects:
                p2_name = asp.p2_name
                pair = tuple(sorted((p1.name, p2_name)) + (asp.aspect_name,))
                if pair not in processed_aspects:
                    aspects_list.append(AspectData(
                        p1_name=p1.name, p1_name_original=p1.name, p1_owner="chart",
                        p2_name=p2_name, p2_name_original=p2_name, p2_owner="chart",
                        aspect=asp.aspect_name, aspect_original=asp.aspect_name,
                        orbit=round(asp.orbit, 4),
                        aspect_degrees=float(asp.aspect_name.split("_")[0]) if "_" in asp.aspect_name else 0.0,
                        diff=abs(round(asp.orbit, 4)), applying=False # Valor padrão
                    ))
                    processed_aspects.add(pair)

        response = NatalChartResponse(
            input_data=request,
            planets=planets_dict,
            houses=houses_dict,
            ascendant=ascendant,
            midheaven=midheaven,
            aspects=aspects_list,
            house_system=request.house_system,
            interpretations=None
        )

        return response

    except Exception as e:
        print(f"Erro de cálculo astrológico em natal_chart (Kerykeion ou outro): {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro de cálculo astrológico (Kerykeion): {str(e)}")



# Modelos para Trânsitos
class TransitAspect(BaseModel):
    transit_planet: str
    natal_planet_or_point: str
    aspect_name: str
    orbit: float

class CurrentTransitsResponse(BaseModel):
    input_data: TransitRequest
    planets: List[PlanetPosition]

class TransitsToNatalRequest(BaseModel):
    natal_data: NatalChartRequest
    transit_data: TransitRequest

class TransitsToNatalResponse(BaseModel):
    natal_input: NatalChartRequest
    transit_input: TransitRequest
    transit_planets_positions: List[PlanetPosition]
    aspects_to_natal: List[TransitAspect]

# Modelos para Gráficos SVG
class SVGChartRequest(BaseModel):
    natal_chart: NatalChartRequest
    transit_chart: Optional[TransitRequest] = None
    chart_type: Literal["natal", "transit", "combined"] = Field(..., description="Tipo de gráfico: natal, trânsito ou combinado")
    theme: str = Field("Kerykeion", description="Tema visual para o gráfico SVG")

    class Config:
        schema_extra = {
            "example": {
                "natal_chart": {
                    "name": "Exemplo Natal",
                    "year": 1990,
                    "month": 1,
                    "day": 1,
                    "hour": 12,
                    "minute": 0,
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "tz_str": "UTC",
                    "house_system": "placidus"
                },
                "transit_chart": {
                    "name": "Exemplo Trânsito",
                    "year": 2024,
                    "month": 1,
                    "day": 1,
                    "hour": 12,
                    "minute": 0,
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "tz_str": "UTC",
                    "house_system": "placidus"
                },
                "chart_type": "combined",
                "theme": "Kerykeion"
            }
        }
