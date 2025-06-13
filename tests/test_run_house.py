import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP
from app.models import NatalChartRequest


def test_planets_not_all_in_house_one():
    request = NatalChartRequest(
        name="Joao Victor - Teste Casas",
        year=1997,
        month=10,
        day=13,
        hour=22,
        minute=0,
        latitude=-3.7319,
        longitude=-38.5434,
        tz_str="America/Fortaleza",
        house_system="placidus",
    )

    subject = create_subject(request, "Teste")

    casa_1_count = 0
    total_planets = 0
    for k_name, api_name in PLANETS_MAP.items():
        planet_data = get_planet_data(subject, k_name, api_name)
        if planet_data:
            if planet_data.house_number == 1:
                casa_1_count += 1
            total_planets += 1

    assert casa_1_count < total_planets, "All planets incorrectly mapped to house 1"
