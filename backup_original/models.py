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

# Modelos para respostas de mapa natal
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

# Modelos para Sinastria
class SynastryRequest(BaseModel):
    person1: NatalChartRequest = Field(..., description="Dados da primeira pessoa")
    person2: NatalChartRequest = Field(..., description="Dados da segunda pessoa")

class SynastryAspect(BaseModel):
    p1_planet: str
    p2_planet: str
    aspect_name: str
    orb: float
    aspect_type: str  # "harmonic", "tense", "neutral"

class SynastryResponse(BaseModel):
    person1_data: NatalChartRequest
    person2_data: NatalChartRequest
    aspects: List[SynastryAspect]
    compatibility_score: float
    summary: str
