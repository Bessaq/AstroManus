from fastapi import APIRouter, HTTPException, Depends
from kerykeion import AstrologicalSubject
from app.models import NatalChartRequest, NatalChartResponse, PlanetData, HouseCuspData, AspectData
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP, HOUSE_NUMBER_TO_NAME_BASE
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix="/api/v1",
    tags=["Natal Chart"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/natal_chart", response_model=NatalChartResponse)
async def create_natal_chart(request: NatalChartRequest):
    try:
        # Usar a função utilitária para criar o subject
        subject = create_subject(request, request.name if request.name else "NatalChart")
        
        # Dicionário para armazenar os planetas
        planets_dict: Dict[str, PlanetData] = {}
        for k_name, api_name in PLANETS_MAP.items():
            planet_data = get_planet_data(subject, k_name, api_name)
            if planet_data:
                # Converter PlanetPosition para PlanetData
                planets_dict[k_name] = PlanetData(
                    name=planet_data.name,
                    name_original=planet_data.name,
                    longitude=planet_data.position,
                    latitude=0.0,  # Valor padrão, não disponível diretamente
                    sign=planet_data.sign,
                    sign_original=planet_data.sign,
                    sign_num=planet_data.sign_num,
                    house=planet_data.house_number,
                    retrograde=planet_data.retrograde
                )
        
        if hasattr(subject, 'chiron') and subject.chiron:
            chiron_data = get_planet_data(subject, 'chiron', 'Chiron')
            if chiron_data:
                planets_dict['chiron'] = PlanetData(
                    name="Chiron",
                    name_original="Chiron",
                    longitude=chiron_data.position,
                    latitude=0.0,
                    sign=chiron_data.sign,
                    sign_original=chiron_data.sign,
                    sign_num=chiron_data.sign_num,
                    house=chiron_data.house_number,
                    retrograde=chiron_data.retrograde
                )
        
        if hasattr(subject, 'lilith') and subject.lilith and subject.lilith.name:
            planets_dict['lilith'] = PlanetData(
                name="Lilith",
                name_original="Lilith",
                longitude=subject.lilith.position,
                latitude=0.0,
                sign=subject.lilith.sign,
                sign_original=subject.lilith.sign,
                sign_num=subject.lilith.sign_num,
                house=subject.lilith.house_number,
                retrograde=False
            )

        # Dicionário para armazenar as casas
        houses_dict: Dict[str, HouseCuspData] = {}
        for i in range(1, 13):
            house_name_base = HOUSE_NUMBER_TO_NAME_BASE.get(i)
            if not house_name_base:
                continue
            
            house_obj_attr_name = f"{house_name_base}_house"
            house_obj = getattr(subject, house_obj_attr_name)
            houses_dict[str(i)] = HouseCuspData(
                number=i,
                sign=house_obj.sign,
                sign_original=house_obj.sign,
                sign_num=getattr(house_obj, 'sign_num', 1),
                longitude=round(house_obj.position, 4)
            )

        # Ascendente e Meio do Céu
        ascendant = HouseCuspData(
            number=1,
            sign=subject.first_house.sign,
            sign_original=subject.first_house.sign,
            sign_num=getattr(subject.first_house, 'sign_num', 1),
            longitude=round(subject.first_house.position, 4)
        )
        
        midheaven = HouseCuspData(
            number=10,
            sign=subject.tenth_house.sign,
            sign_original=subject.tenth_house.sign,
            sign_num=getattr(subject.tenth_house, 'sign_num', 1),
            longitude=round(subject.tenth_house.position, 4)
        )

        # Lista para armazenar os aspectos
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
                        p1_name=p1.name,
                        p1_name_original=p1.name,
                        p1_owner="chart",
                        p2_name=p2_name,
                        p2_name_original=p2_name,
                        p2_owner="chart",
                        aspect=asp.aspect_name,
                        aspect_original=asp.aspect_name,
                        orbit=round(asp.orbit, 4),
                        aspect_degrees=float(asp.aspect_name.split("_")[0]) if "_" in asp.aspect_name else 0.0,
                        diff=abs(round(asp.orbit, 4)),
                        applying=False  # Valor padrão, não disponível diretamente
                    ))
                    processed_aspects.add(pair)
        
        # Criar o objeto de resposta
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
