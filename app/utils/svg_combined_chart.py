"""
Módulo para geração de SVG combinado de mapa natal e trânsitos com aspectos.

Este módulo implementa uma solução personalizada para gerar SVGs que mostram
visualmente os aspectos entre um mapa natal e os planetas em trânsito.
"""
import math
import svgwrite
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from kerykeion import AstrologicalSubject

# Constantes para o desenho do SVG
CHART_SIZE = 800  # Tamanho do SVG em pixels
CHART_CENTER = CHART_SIZE / 2
ZODIAC_RADIUS = CHART_SIZE * 0.35  # Raio do círculo zodiacal
PLANET_RADIUS_NATAL = ZODIAC_RADIUS * 0.75  # Raio para posicionar planetas natais
PLANET_RADIUS_TRANSIT = ZODIAC_RADIUS * 0.6  # Raio para posicionar planetas em trânsito

# Cores para diferentes tipos de aspectos
ASPECT_COLORS = {
    "Conjunção": "#FF0000",      # Vermelho
    "Oposição": "#0000FF",       # Azul
    "Trígono": "#00FF00",        # Verde
    "Quadratura": "#FF00FF",     # Magenta
    "Sextil": "#FFFF00",         # Amarelo
    "Quincúncio": "#00FFFF",     # Ciano
    "Semi-Sextil": "#FFA500",    # Laranja
    "Semi-Quadratura": "#800080", # Roxo
    "Sesqui-Quadratura": "#008080", # Teal
    "Quintil": "#800000",        # Marrom
    "Bi-Quintil": "#808000"      # Oliva
}

# Símbolos dos planetas
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "Chiron": "⚷", "Lilith": "⚸", "North Node": "☊", "South Node": "☋"
}

# Símbolos dos signos
SIGN_SYMBOLS = {
    "Ari": "♈", "Tau": "♉", "Gem": "♊", "Can": "♋", "Leo": "♌", "Vir": "♍",
    "Lib": "♎", "Sco": "♏", "Sag": "♐", "Cap": "♑", "Aqu": "♒", "Pis": "♓"
}

def calculate_point_on_circle(center_x: float, center_y: float, radius: float, angle_deg: float) -> Tuple[float, float]:
    """
    Calcula as coordenadas de um ponto em um círculo dado o ângulo em graus.
    
    Args:
        center_x: Coordenada X do centro do círculo
        center_y: Coordenada Y do centro do círculo
        radius: Raio do círculo
        angle_deg: Ângulo em graus (0° = direita, sentido anti-horário)
        
    Returns:
        Tupla (x, y) com as coordenadas do ponto
    """
    # Converter graus para radianos e ajustar para o sistema de coordenadas SVG
    # No SVG, 0° está à direita e aumenta no sentido horário
    # Na astrologia, 0° está à direita (Áries) e aumenta no sentido anti-horário
    angle_rad = math.radians(90 - angle_deg)
    
    x = center_x + radius * math.cos(angle_rad)
    y = center_y - radius * math.sin(angle_rad)
    
    return (x, y)

def get_planet_position_angle(planet) -> float:
    """
    Obtém o ângulo absoluto de um planeta no zodíaco.
    
    Args:
        planet: Objeto planeta do Kerykeion
        
    Returns:
        Ângulo em graus (0-360)
    """
    return planet.abs_pos

def draw_zodiac_wheel(dwg, center_x: float, center_y: float, radius: float):
    """
    Desenha o círculo zodiacal com os 12 signos.
    
    Args:
        dwg: Objeto SVG do svgwrite
        center_x: Coordenada X do centro do círculo
        center_y: Coordenada Y do centro do círculo
        radius: Raio do círculo zodiacal
    """
    # Desenhar círculo externo do zodíaco
    dwg.add(dwg.circle(center=(center_x, center_y), r=radius, 
                      fill='none', stroke='black', stroke_width=2))
    
    # Desenhar divisões dos signos (cada 30 graus)
    for i in range(12):
        angle_deg = i * 30
        start_point = calculate_point_on_circle(center_x, center_y, radius, angle_deg)
        end_point = (center_x, center_y)
        dwg.add(dwg.line(start=start_point, end=end_point, 
                        stroke='black', stroke_width=1, stroke_dasharray="5,5"))
        
        # Adicionar símbolo do signo
        sign_angle = angle_deg + 15  # Centro do signo (15° dentro do setor de 30°)
        sign_point = calculate_point_on_circle(center_x, center_y, radius * 1.1, sign_angle)
        sign_name = list(SIGN_SYMBOLS.keys())[i]
        sign_symbol = SIGN_SYMBOLS[sign_name]
        
        dwg.add(dwg.text(sign_symbol, insert=sign_point, 
                        font_size=24, text_anchor="middle", dominant_baseline="middle"))

def draw_planet(dwg, center_x: float, center_y: float, radius: float, 
               planet, is_transit: bool = False):
    """
    Desenha um planeta no gráfico.
    
    Args:
        dwg: Objeto SVG do svgwrite
        center_x: Coordenada X do centro do círculo
        center_y: Coordenada Y do centro do círculo
        radius: Raio para posicionar o planeta
        planet: Objeto planeta do Kerykeion
        is_transit: Se True, é um planeta em trânsito; se False, é natal
    """
    angle = get_planet_position_angle(planet)
    position = calculate_point_on_circle(center_x, center_y, radius, angle)
    
    # Determinar cor e estilo com base no tipo (natal ou trânsito)
    color = "blue" if is_transit else "black"
    bg_color = "lightblue" if is_transit else "white"
    
    # Desenhar círculo de fundo para o planeta
    dwg.add(dwg.circle(center=position, r=12, 
                      fill=bg_color, stroke=color, stroke_width=1))
    
    # Adicionar símbolo do planeta
    planet_name = planet.name.split()[0]  # Pegar apenas a primeira palavra (ex: "Sun" de "Sun in Aries")
    symbol = PLANET_SYMBOLS.get(planet_name, "?")
    
    dwg.add(dwg.text(symbol, insert=position, 
                    font_size=16, text_anchor="middle", dominant_baseline="middle",
                    fill=color))
    
    # Adicionar pequeno texto com o nome do planeta para legenda
    label_position = calculate_point_on_circle(position[0], position[1], 20, angle)
    dwg.add(dwg.text(planet_name, insert=label_position, 
                    font_size=10, text_anchor="middle", dominant_baseline="middle",
                    fill=color))
    
    return position, planet_name

def draw_aspect_line(dwg, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                    aspect_name: str):
    """
    Desenha uma linha de aspecto entre dois planetas.
    
    Args:
        dwg: Objeto SVG do svgwrite
        start_pos: Posição (x, y) do primeiro planeta
        end_pos: Posição (x, y) do segundo planeta
        aspect_name: Nome do aspecto (ex: "Conjunção", "Trígono")
    """
    color = ASPECT_COLORS.get(aspect_name, "#999999")  # Cinza como cor padrão
    
    # Definir estilo da linha com base no tipo de aspecto
    stroke_width = 1
    stroke_dasharray = None
    
    if aspect_name in ["Conjunção", "Oposição"]:
        stroke_width = 2  # Linha mais grossa para aspectos maiores
    elif aspect_name in ["Trígono", "Sextil"]:
        stroke_dasharray = "5,3"  # Linha tracejada para aspectos harmônicos
    elif aspect_name in ["Quadratura", "Quincúncio"]:
        stroke_dasharray = "2,2"  # Linha pontilhada para aspectos tensos
    
    # Desenhar a linha de aspecto
    line = dwg.line(start=start_pos, end=end_pos, stroke=color, stroke_width=stroke_width)
    if stroke_dasharray:
        line.attribs["stroke-dasharray"] = stroke_dasharray
    
    dwg.add(line)

def create_combined_chart_svg(natal_subject: AstrologicalSubject, 
                             transit_subject: AstrologicalSubject,
                             output_path: Path) -> str:
    """
    Cria um SVG combinado mostrando o mapa natal e os trânsitos com aspectos.
    
    Args:
        natal_subject: Objeto AstrologicalSubject do mapa natal
        transit_subject: Objeto AstrologicalSubject dos trânsitos
        output_path: Caminho para salvar o arquivo SVG
        
    Returns:
        Caminho do arquivo SVG gerado
    """
    # Criar o objeto SVG
    dwg = svgwrite.Drawing(str(output_path), size=(CHART_SIZE, CHART_SIZE))
    
    # Adicionar retângulo de fundo branco para melhor visualização
    dwg.add(dwg.rect(insert=(0, 0), size=(CHART_SIZE, CHART_SIZE), fill='white'))
    
    # Adicionar título
    title = f"{natal_subject.name} - Mapa Natal com Trânsitos de {transit_subject.name}"
    dwg.add(dwg.text(title, insert=(CHART_SIZE/2, 30), 
                    font_size=20, text_anchor="middle", font_weight="bold"))
    
    # Desenhar o círculo zodiacal
    draw_zodiac_wheel(dwg, CHART_CENTER, CHART_CENTER, ZODIAC_RADIUS)
    
    # Dicionário para armazenar posições dos planetas para desenhar aspectos depois
    planet_positions = {}
    
    # Desenhar planetas natais
    natal_planets = [
        natal_subject.sun, natal_subject.moon, natal_subject.mercury, 
        natal_subject.venus, natal_subject.mars, natal_subject.jupiter, 
        natal_subject.saturn, natal_subject.uranus, natal_subject.neptune, 
        natal_subject.pluto
    ]
    
    for planet in natal_planets:
        if not planet or not hasattr(planet, 'abs_pos'):
            continue
        position, name = draw_planet(dwg, CHART_CENTER, CHART_CENTER, PLANET_RADIUS_NATAL, planet, is_transit=False)
        planet_positions[f"natal_{name}"] = position
    
    # Desenhar planetas em trânsito
    transit_planets = [
        transit_subject.sun, transit_subject.moon, transit_subject.mercury, 
        transit_subject.venus, transit_subject.mars, transit_subject.jupiter, 
        transit_subject.saturn, transit_subject.uranus, transit_subject.neptune, 
        transit_subject.pluto
    ]
    
    for planet in transit_planets:
        if not planet or not hasattr(planet, 'abs_pos'):
            continue
        position, name = draw_planet(dwg, CHART_CENTER, CHART_CENTER, PLANET_RADIUS_TRANSIT, planet, is_transit=True)
        planet_positions[f"transit_{name}"] = position
    
    # Definir aspectos e suas orbes
    aspect_types = {
        "Conjunção": (0, 8),    # (graus, orbe máxima)
        "Oposição": (180, 8),
        "Trígono": (120, 8),
        "Quadratura": (90, 7),
        "Sextil": (60, 6),
        "Quincúncio": (150, 5),
        "Semi-Sextil": (30, 3),
        "Semi-Quadratura": (45, 3),
        "Sesqui-Quadratura": (135, 3),
        "Quintil": (72, 2),
        "Bi-Quintil": (144, 2)
    }
    
    # Calcular e desenhar aspectos entre planetas natais e de trânsito
    aspects_found = []
    for transit_planet in transit_planets:
        if not transit_planet or not hasattr(transit_planet, 'abs_pos'):
            continue
            
        for natal_planet in natal_planets:
            if not natal_planet or not hasattr(natal_planet, 'abs_pos'):
                continue
                
            # Calcular diferença entre posições
            diff = abs(natal_planet.abs_pos - transit_planet.abs_pos)
            if diff > 180:
                diff = 360 - diff
            
            # Verificar se forma algum aspecto
            for aspect_name, (aspect_angle, max_orb) in aspect_types.items():
                orb = abs(diff - aspect_angle)
                if orb <= max_orb:
                    aspects_found.append({
                        "transit_planet": transit_planet.name.split()[0],
                        "natal_planet": natal_planet.name.split()[0],
                        "aspect": aspect_name,
                        "orb": round(orb, 2)
                    })
                    
                    # Desenhar linha de aspecto
                    start_pos = planet_positions.get(f"transit_{transit_planet.name.split()[0]}")
                    end_pos = planet_positions.get(f"natal_{natal_planet.name.split()[0]}")
                    
                    if start_pos and end_pos:
                        draw_aspect_line(dwg, start_pos, end_pos, aspect_name)
    
    # Adicionar legenda
    legend_y = CHART_SIZE - 120
    dwg.add(dwg.text("Legenda:", insert=(50, legend_y), font_size=16, font_weight="bold"))
    
    # Legenda para planetas
    dwg.add(dwg.text("Planetas Natais:", insert=(50, legend_y + 25), font_size=14))
    dwg.add(dwg.circle(center=(70, legend_y + 45), r=8, fill="white", stroke="black"))
    
    dwg.add(dwg.text("Planetas em Trânsito:", insert=(50, legend_y + 65), font_size=14))
    dwg.add(dwg.circle(center=(70, legend_y + 85), r=8, fill="lightblue", stroke="blue"))
    
    # Legenda para aspectos
    aspect_legend_x = 250
    dwg.add(dwg.text("Aspectos:", insert=(aspect_legend_x, legend_y + 25), font_size=14))
    
    y_offset = 45
    for aspect_name, color in list(ASPECT_COLORS.items())[:6]:  # Mostrar apenas os principais aspectos
        dwg.add(dwg.line(start=(aspect_legend_x, legend_y + y_offset), 
                        end=(aspect_legend_x + 40, legend_y + y_offset), 
                        stroke=color, stroke_width=2))
        dwg.add(dwg.text(aspect_name, insert=(aspect_legend_x + 50, legend_y + y_offset + 5), 
                        font_size=12))
        y_offset += 20
    
    # Salvar o SVG
    dwg.save()
    
    return str(output_path)

def generate_combined_chart(natal_subject: AstrologicalSubject, 
                           transit_subject: AstrologicalSubject,
                           output_dir: Path) -> str:
    """
    Gera um gráfico SVG combinado de mapa natal e trânsitos.
    
    Args:
        natal_subject: Objeto AstrologicalSubject do mapa natal
        transit_subject: Objeto AstrologicalSubject dos trânsitos
        output_dir: Diretório para salvar o arquivo SVG
        
    Returns:
        Caminho do arquivo SVG gerado
    """
    # Criar diretório se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Definir nome do arquivo
    file_name = f"{natal_subject.name}_com_transitos_{transit_subject.name}.svg"
    output_path = output_dir / file_name
    
    # Criar o SVG
    return create_combined_chart_svg(natal_subject, transit_subject, output_path)
