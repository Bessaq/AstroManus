from kerykeion import AstrologicalSubject
from pathlib import Path
import sys
import os
import re

# Adicionar o diretório raiz ao path para importar módulos do app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Função para sanitizar nomes de arquivos
def sanitize_filename(filename):
    # Remover caracteres especiais e espaços
    sanitized = re.sub(r'[^\w\-_]', '_', filename)
    return sanitized

# Modificar a função generate_combined_chart para sanitizar nomes de arquivos
def generate_combined_chart(natal_subject, transit_subject, output_dir):
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
    
    # Sanitizar nomes para o arquivo
    natal_name = sanitize_filename(natal_subject.name)
    transit_name = sanitize_filename(transit_subject.name)
    
    # Definir nome do arquivo
    file_name = f"{natal_name}_com_transitos_{transit_name}.svg"
    output_path = output_dir / file_name
    
    # Importar a função original após a definição da função sanitize_filename
    from app.utils.svg_combined_chart import create_combined_chart_svg
    
    # Criar o SVG
    return create_combined_chart_svg(natal_subject, transit_subject, output_path)

# Dados do mapa natal de João
natal_subject = AstrologicalSubject(
    name='João',
    year=1997,
    month=10,
    day=13,
    hour=22,
    minute=0,
    city='Fortaleza',
    lng=-38.5247,
    lat=-3.7172,
    tz_str='America/Fortaleza'
)

# Dados dos trânsitos para 02/06/2025
transit_subject = AstrologicalSubject(
    name='Transitos_02_06_2025',
    year=2025,
    month=6,
    day=2,
    hour=12,
    minute=0,
    city='Fortaleza',
    lng=-38.5247,
    lat=-3.7172,
    tz_str='America/Fortaleza'
)

# Diretório para salvar o SVG
output_dir = Path("/tmp/astro_svg")

# Gerar o SVG combinado
svg_path = generate_combined_chart(natal_subject, transit_subject, output_dir)
print(f"SVG combinado gerado com sucesso: {svg_path}")
