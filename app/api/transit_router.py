from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.models import (
    TransitRequest, CurrentTransitsResponse,
    TransitsToNatalRequest, TransitsToNatalResponse,
    PlanetPosition, TransitAspect, NatalChartRequest
)
from app.security import verify_api_key
from app.utils.astro_helpers import (
    create_subject,
    get_planet_data,
    PLANETS_MAP,
    get_house_from_kerykeion_attribute,
)
from typing import List, Optional

router = APIRouter(
    prefix="/api/v1",
    tags=["Transits"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/current_transits", response_model=CurrentTransitsResponse)
async def get_current_transits(request: TransitRequest):
    try:
        # Usar a função utilitária para criar o subject
        transit_subject = create_subject(request, "CurrentTransits")

        transit_planets: List[PlanetPosition] = []
        for k_name, api_name in PLANETS_MAP.items():
            planet_data = get_planet_data(transit_subject, k_name, api_name)
            if planet_data:
                transit_planets.append(planet_data)

        if hasattr(transit_subject, 'chiron') and transit_subject.chiron:
            chiron_data = get_planet_data(transit_subject, 'chiron', 'Chiron')
            if chiron_data: transit_planets.append(chiron_data)

        if hasattr(transit_subject, 'lilith') and transit_subject.lilith and transit_subject.lilith.name:
            lilith_data = PlanetPosition(
                name="Lilith",
                sign=transit_subject.lilith.sign,
                sign_num=transit_subject.lilith.sign_num,
                position=round(transit_subject.lilith.position, 4),
                abs_pos=round(transit_subject.lilith.abs_pos, 4),
                house_number=get_house_from_kerykeion_attribute(transit_subject.lilith),
                speed=0.0,
                retrograde=False,
            )
            transit_planets.append(lilith_data)

        return CurrentTransitsResponse(input_data=request, planets=transit_planets)

    except Exception as e:
        print(f"Erro de cálculo astrológico em current_transits (Kerykeion ou outro): {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro de cálculo astrológico (Kerykeion): {str(e)}")

@router.post("/transits_to_natal", response_model=TransitsToNatalResponse)
async def get_transits_to_natal(request: TransitsToNatalRequest):
    try:
        # Usar a função utilitária para criar os subjects
        natal_subject = create_subject(request.natal_data,
                                      request.natal_data.name if request.natal_data.name else "NatalChart")
        transit_subject = create_subject(request.transit_data, "TransitChart")

        transit_planets_positions: List[PlanetPosition] = []
        for k_name, api_name in PLANETS_MAP.items():
            planet_data = get_planet_data(transit_subject, k_name, api_name)
            if planet_data:
                transit_planets_positions.append(planet_data)

        if hasattr(transit_subject, 'chiron') and transit_subject.chiron:
            chiron_data = get_planet_data(transit_subject, 'chiron', 'Chiron')
            if chiron_data: transit_planets_positions.append(chiron_data)

        # Calcular aspectos manualmente já que get_aspects_to não está disponível na versão atual
        aspects_to_natal: List[TransitAspect] = []

        # Planetas natais para verificar aspectos
        natal_planets = [
            natal_subject.sun, natal_subject.moon, natal_subject.mercury,
            natal_subject.venus, natal_subject.mars, natal_subject.jupiter,
            natal_subject.saturn, natal_subject.uranus, natal_subject.neptune,
            natal_subject.pluto
        ]

        # Planetas de trânsito para verificar aspectos
        transit_planets = [
            transit_subject.sun, transit_subject.moon, transit_subject.mercury,
            transit_subject.venus, transit_subject.mars, transit_subject.jupiter,
            transit_subject.saturn, transit_subject.uranus, transit_subject.neptune,
            transit_subject.pluto
        ]

        # Definir aspectos e suas orbes
        aspect_types = {
            "Conjunction": (0, 8),    # (graus, orbe máxima)
            "Opposition": (180, 8),
            "Trine": (120, 8),
            "Square": (90, 7),
            "Sextile": (60, 6),
            "Quincunx": (150, 5),
            "Semi-Sextile": (30, 3),
            "Semi-Square": (45, 3),
            "Sesqui-Square": (135, 3),
            "Quintile": (72, 2),
            "Bi-Quintile": (144, 2)
        }

        # Calcular aspectos entre planetas natais e de trânsito
        for natal_planet in natal_planets:
            if not natal_planet or not hasattr(natal_planet, 'abs_pos'):
                continue

            for transit_planet in transit_planets:
                if not transit_planet or not hasattr(transit_planet, 'abs_pos'):
                    continue

                # Calcular diferença entre posições
                diff = abs(natal_planet.abs_pos - transit_planet.abs_pos)
                if diff > 180:
                    diff = 360 - diff

                # Verificar se forma algum aspecto
                for aspect_name, (aspect_angle, max_orb) in aspect_types.items():
                    orb = abs(diff - aspect_angle)
                    if orb <= max_orb:
                        aspects_to_natal.append(TransitAspect(
                            transit_planet=transit_planet.name,
                            natal_planet_or_point=natal_planet.name,
                            aspect_name=aspect_name,
                            orbit=round(orb, 4)
                        ))

        return TransitsToNatalResponse(
            natal_input=request.natal_data,
            transit_input=request.transit_data,
            transit_planets_positions=transit_planets_positions,
            aspects_to_natal=aspects_to_natal
        )

    except Exception as e:
        print(f"Erro de cálculo astrológico em transits_to_natal (Kerykeion ou outro): {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro de cálculo astrológico (Kerykeion): {str(e)}")
