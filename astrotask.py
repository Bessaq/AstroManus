 #!/usr/bin/env python3
"""
Astrotask - Script universal para execução de tarefas astrológicas via Kestra
Permite execução de cálculos astrológicos via linha de comando com saída em JSON
"""

import argparse
import json
import sys
import os
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Logs vão para stderr
    ]
)
logger = logging.getLogger(__name__)

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from kerykeion import AstrologicalSubject
    from app.models import NatalChartRequest, TransitRequest, HouseSystem
    from app.utils.astro_helpers import create_subject, get_planet_data, PLANETS_MAP
    from app.utils.svg_combined_chart import create_combined_chart_svg
    logger.info("✅ Dependências carregadas com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro ao importar dependências: {e}")
    sys.exit(1)

class AstroTaskExecutor:
    """Executor de tarefas astrológicas para Kestra"""
    
    def __init__(self):
        self.output_dir = Path(os.getenv('OUTPUT_DIR', '/app/output'))
        self.cache_dir = Path(os.getenv('CACHE_DIR', '/app/cache'))
        self.temp_dir = Path(os.getenv('TEMP_DIR', '/app/temp'))
        
        # Criar diretórios se não existirem
        for dir_path in [self.output_dir, self.cache_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def execute_natal_chart(self, **kwargs) -> Dict[str, Any]:
        """Gera mapa natal completo"""
        logger.info(f"🌟 Calculando mapa natal para {kwargs.get('name', 'Usuário')}")
        
        try:
            # Criar request object
            request = NatalChartRequest(
                name=kwargs.get('name', 'Desconhecido'),
                year=int(kwargs['year']),
                month=int(kwargs['month']),
                day=int(kwargs['day']),
                hour=int(kwargs['hour']),
                minute=int(kwargs['minute']),
                latitude=float(kwargs['latitude']),
                longitude=float(kwargs['longitude']),
                tz_str=kwargs['tz_str'],
                house_system=HouseSystem(kwargs.get('house_system', 'placidus'))
            )
            
            # Criar subject usando helper
            subject = create_subject(request, request.name)
            
            # Extrair dados dos planetas
            planets_data = {}
            for k_name, api_name in PLANETS_MAP.items():
                planet_data = get_planet_data(subject, k_name, api_name)
                if planet_data:
                    planets_data[k_name] = {
                        "name": planet_data.name,
                        "sign": planet_data.sign,
                        "sign_num": planet_data.sign_num,
                        "position": planet_data.position,
                        "abs_pos": planet_data.abs_pos,
                        "house_number": planet_data.house_number,
                        "speed": planet_data.speed,
                        "retrograde": planet_data.retrograde
                    }
            
            # Resultado completo
            result = {
                "user_info": {
                    "name": request.name,
                    "birth_date": f"{request.year}-{request.month:02d}-{request.day:02d}",
                    "birth_time": f"{request.hour:02d}:{request.minute:02d}",
                    "location": {
                        "latitude": request.latitude,
                        "longitude": request.longitude,
                        "timezone": request.tz_str
                    },
                    "house_system": request.house_system
                },
                "planets": planets_data,
                "houses": {
                    f"house_{i}": getattr(subject, f"house{i}", {}).get('position', 0)
                    for i in range(1, 13)
                },
                "metadata": {
                    "calculated_at": datetime.now().isoformat(),
                    "total_planets": len(planets_data),
                    "kerykeion_version": "4.26.2"
                }
            }
            
            logger.info(f"✅ Mapa natal calculado - {len(planets_data)} planetas")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular mapa natal: {e}")
            logger.error(traceback.format_exc())
            raise

def execute_daily_transits(self, **kwargs) -> Dict[str, Any]:
        """Calcula trânsitos diários"""
        date_str = kwargs.get('date')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str)
            except:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date_obj = datetime.now()
        
        logger.info(f"📅 Calculando trânsitos para {date_obj.strftime('%d/%m/%Y')}")
        
        try:
            # Criar request para trânsitos
            transit_request = TransitRequest(
                year=date_obj.year,
                month=date_obj.month,
                day=date_obj.day,
                hour=12,  # Meio-dia como padrão
                minute=0,
                latitude=kwargs.get('latitude', -15.7939),  # Brasília como padrão
                longitude=kwargs.get('longitude', -47.8828),
                tz_str=kwargs.get('tz_str', 'America/Sao_Paulo')
            )
            
            # Criar subject para trânsitos
            subject = create_subject(transit_request, f"Trânsitos {date_str}")
            
            # Extrair posições planetárias
            transit_positions = {}
            for k_name, api_name in PLANETS_MAP.items():
                planet_data = get_planet_data(subject, k_name, api_name)
                if planet_data:
                    transit_positions[k_name] = {
                        "name": planet_data.name,
                        "sign": planet_data.sign,
                        "position": planet_data.position,
                        "retrograde": planet_data.retrograde
                    }
            
            # Calcular aspectos principais
            aspects = self._calculate_transit_aspects(transit_positions)
            
            result = {
                "date": date_obj.strftime('%Y-%m-%d'),
                "transit_positions": transit_positions,
                "aspects": aspects,
                "summary": {
                    "total_aspects": len(aspects),
                    "major_aspects": len([a for a in aspects if a['type'] in ['conjunction', 'opposition', 'trine', 'square']]),
                    "retrograde_planets": [p for p, data in transit_positions.items() if data.get('retrograde', False)]
                },
                "metadata": {
                    "calculated_at": datetime.now().isoformat(),
                    "reference_location": {
                        "latitude": transit_request.latitude,
                        "longitude": transit_request.longitude,
                        "timezone": transit_request.tz_str
                    }
                }
            }
            
            logger.info(f"✅ Trânsitos calculados - {len(aspects)} aspectos encontrados")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular trânsitos: {e}")
            logger.error(traceback.format_exc())
            raise

    def _calculate_transit_aspects(self, transit_positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calcula aspectos entre planetas em trânsito"""
        aspects = []
        planets = list(transit_positions.keys())
        
        # Aspectos principais e suas tolerâncias
        aspect_definitions = {
            0: ("conjunction", 8),
            60: ("sextile", 6),
            90: ("square", 7),
            120: ("trine", 8),
            180: ("opposition", 8)
        }
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                pos1 = transit_positions[planet1]['position']
                pos2 = transit_positions[planet2]['position']
                
                # Calcular diferença angular
                diff = abs(pos1 - pos2)
                if diff > 180:
                    diff = 360 - diff
                
                # Verificar aspectos
                for aspect_angle, (aspect_name, orb_tolerance) in aspect_definitions.items():
                    orb = abs(diff - aspect_angle)
                    if orb <= orb_tolerance:
                        aspects.append({
                            "p1": transit_positions[planet1]['name'],
                            "p2": transit_positions[planet2]['name'],
                            "type": aspect_name,
                            "orb": round(orb, 2),
                            "exact_angle": round(diff, 2),
                            "strength": round((orb_tolerance - orb) / orb_tolerance * 100, 1)
                        })
        
        # Ordenar por força do aspecto
        aspects.sort(key=lambda x: x['strength'], reverse=True)
        return aspects

def main():
    """Função principal - entrada do script"""
    parser = argparse.ArgumentParser(
        description='Astrotask - Executor de tarefas astrológicas para Kestra',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos de uso:

# Mapa natal
python astrotask.py --task natal_chart --name "João" --year 1997 --month 10 --day 13 --hour 22 --minute 0 --latitude -3.7172 --longitude -38.5247 --tz-str "America/Fortaleza"

# Trânsitos diários
python astrotask.py --task daily_transits --date "2025-06-13"
        '''
    )
    
    # Argumentos principais
    parser.add_argument('--task', required=True, 
                       choices=['natal_chart', 'daily_transits', 'weekly_transits', 'moon_phase', 'combined_svg'],
                       help='Tarefa a ser executada')
    
    # Argumentos para mapa natal
    parser.add_argument('--name', help='Nome da pessoa')
    parser.add_argument('--year', type=int, help='Ano de nascimento')
    parser.add_argument('--month', type=int, help='Mês de nascimento')
    parser.add_argument('--day', type=int, help='Dia de nascimento')
    parser.add_argument('--hour', type=int, help='Hora de nascimento')
    parser.add_argument('--minute', type=int, help='Minuto de nascimento')
    parser.add_argument('--latitude', type=float, help='Latitude')
    parser.add_argument('--longitude', type=float, help='Longitude')
    parser.add_argument('--tz-str', help='Timezone string (ex: America/Sao_Paulo)')
    parser.add_argument('--house-system', default='placidus', help='Sistema de casas')
    
    # Argumentos para trânsitos
    parser.add_argument('--date', help='Data para cálculos (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        executor = AstroTaskExecutor()
        
        # Preparar argumentos
        kwargs = {}
        for key, value in vars(args).items():
            if value is not None and key not in ['task']:
                kwargs[key.replace('_', '-')] = value
        
        # Executar tarefa
        logger.info(f"🚀 Executando tarefa: {args.task}")
        
        if args.task == 'natal_chart':
            result = executor.execute_natal_chart(**kwargs)
        elif args.task == 'daily_transits':
            result = executor.execute_daily_transits(**kwargs)
        else:
            raise ValueError(f"Tarefa não implementada: {args.task}")
        
        # Imprimir resultado no stdout (para Kestra capturar)
        print(json.dumps(result, ensure_ascii=False))
        
        logger.info(f"✅ Tarefa {args.task} executada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro na execução: {e}")
        
        # Retornar erro em formato JSON para Kestra
        error_result = {
            "error": True,
            "message": str(e),
            "task": args.task,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()