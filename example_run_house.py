#!/usr/bin/env python3
"""
Teste direto das casas corrigidas
"""
import sys
import os
sys.path.append('.')

from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP
from app.models import NatalChartRequest

# Criar requisição
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
    house_system="placidus"
)

# Criar subject
subject = create_subject(request, "Teste")

print("=== TESTE DIRETO DAS CASAS ===")
print(f"Subject: {subject.name}")

# Testar cada planeta
casa_1_count = 0
total_planets = 0

for k_name, api_name in PLANETS_MAP.items():
    planet_data = get_planet_data(subject, k_name, api_name)
    if planet_data:
        print(f"{api_name}: Casa {planet_data.house_number} - {planet_data.sign}") # Changed house to house_number
        if planet_data.house_number == 1: # Changed house to house_number
            casa_1_count += 1
        total_planets += 1

print(f"\nPlanetas na casa 1: {casa_1_count} de {total_planets}")

if casa_1_count == total_planets:
    print("❌ ERRO: Todos os planetas ainda estão na casa 1!")
else:
    print("✅ SUCESSO: Casas calculadas corretamente!")
