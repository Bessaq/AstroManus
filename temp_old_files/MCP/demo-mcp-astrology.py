#!/usr/bin/env python3
"""
Demonstração do Servidor MCP de Astrologia
Este script mostra como usar todas as funcionalidades do servidor MCP
"""

import json
from datetime import datetime

def demo_natal_chart():
    """Demonstra o cálculo de mapa natal"""
    print("🌟 DEMO: Cálculo de Mapa Natal")
    print("=" * 40)
    
    request = {
        "tool": "calculate_natal_chart",
        "arguments": {
            "name": "João da Silva",
            "year": 1990,
            "month": 3,
            "day": 21,  # Nasceu no equinócio de primavera
            "hour": 6,   # Nascer do sol
            "minute": 0,
            "latitude": -23.5505,  # São Paulo
            "longitude": -46.6333,
            "tz_str": "America/Sao_Paulo",
            "house_system": "placidus"
        }
    }
    
    print("📋 Requisição:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    print("📊 Resultado esperado:")
    print("• Planetas em signos e casas")
    print("• Ascendente e Meio do Céu")
    print("• Aspectos entre planetas")
    print("• Sistema de casas utilizado")
    print()

def demo_current_transits():
    """Demonstra consulta de trânsitos atuais"""
    print("🌙 DEMO: Trânsitos Atuais")
    print("=" * 40)
    
    now = datetime.now()
    
    request = {
        "tool": "get_current_transits",
        "arguments": {
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": 12,  # Meio-dia
            "minute": 0,
            "latitude": -23.5505,  # São Paulo
            "longitude": -46.6333,
            "tz_str": "America/Sao_Paulo",
            "name": f"Trânsitos {now.strftime('%d/%m/%Y')}"
        }
    }
    
    print("📋 Requisição:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    print("📊 Resultado esperado:")
    print("• Posições planetárias atuais")
    print("• Signos e graus de cada planeta")
    print("• Indicação de planetas retrógrados")
    print()

def demo_transits_to_natal():
    """Demonstra cálculo de aspectos trânsito-natal"""
    print("🔮 DEMO: Aspectos Trânsito-Natal")
    print("=" * 40)
    
    request = {
        "tool": "calculate_transits_to_natal",
        "arguments": {
            "natal_data": {
                "name": "Maria Santos",
                "year": 1985,
                "month": 7,
                "day": 15,
                "hour": 9,
                "minute": 30,
                "latitude": -22.9068,  # Rio de Janeiro
                "longitude": -43.1729,
                "tz_str": "America/Sao_Paulo",
                "house_system": "placidus"
            },
            "transit_data": {
                "year": 2025,
                "month": 6,
                "day": 5,
                "hour": 18,
                "minute": 0,
                "latitude": -22.9068,  # Rio de Janeiro
                "longitude": -43.1729,
                "tz_str": "America/Sao_Paulo",
                "name": "Trânsitos para Maria"
            }
        }
    }
    
    print("📋 Requisição:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    print("📊 Resultado esperado:")
    print("• Planetas em trânsito atuais")
    print("• Aspectos aos planetas natais")
    print("• Orbes dos aspectos")
    print("• Interpretação dos aspectos")
    print()

def demo_svg_chart():
    """Demonstra geração de gráfico SVG"""
    print("🎨 DEMO: Gráfico SVG")
    print("=" * 40)
    
    request = {
        "tool": "generate_svg_chart",
        "arguments": {
            "natal_chart": {
                "name": "Carlos Poeta",
                "year": 1975,
                "month": 12,
                "day": 25,  # Natal
                "hour": 0,   # Meia-noite
                "minute": 0,
                "latitude": -15.7801,  # Brasília
                "longitude": -47.9292,
                "tz_str": "America/Sao_Paulo",
                "house_system": "placidus"
            },
            "chart_type": "natal",
            "theme": "Kerykeion",
            "return_base64": False
        }
    }
    
    print("📋 Requisição:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    print("📊 Resultado esperado:")
    print("• Gráfico astrológico em formato SVG")
    print("• Visualização completa do mapa")
    print("• Planetas, casas e aspectos")
    print("• Tema visual aplicado")
    print()

def demo_combined_svg():
    """Demonstra gráfico SVG combinado"""
    print("🌟 DEMO: Gráfico SVG Combinado")
    print("=" * 40)
    
    request = {
        "tool": "generate_combined_svg_chart",
        "arguments": {
            "natal_chart": {
                "name": "Ana Cosmóloga",
                "year": 1988,
                "month": 4,
                "day": 22,  # Dia da Terra
                "hour": 12,
                "minute": 0,
                "latitude": -8.0476,  # Recife
                "longitude": -34.8770,
                "tz_str": "America/Recife",
                "house_system": "placidus"
            },
            "transit_chart": {
                "year": 2025,
                "month": 6,
                "day": 21,  # Solstício
                "hour": 12,
                "minute": 0,
                "latitude": -8.0476,  # Recife
                "longitude": -34.8770,
                "tz_str": "America/Recife",
                "name": "Solstício 2025"
            },
            "return_base64": True
        }
    }
    
    print("📋 Requisição:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    print("📊 Resultado esperado:")
    print("• Gráfico combinado natal + trânsitos")
    print("• Aspectos entre os dois mapas")
    print("• Visualização especializada")
    print("• Retorno em base64 para web")
    print()

def demo_interpretation():
    """Demonstra interpretação astrológica"""
    print("🔮 DEMO: Interpretação Astrológica")
    print("=" * 40)
    
    # Exemplo de dados de mapa natal para interpretação
    chart_data = {
        "planets": {
            "sun": {"sign": "Aries", "house": 1},
            "moon": {"sign": "Cancer", "house": 4},
            "mercury": {"sign": "Aries", "house": 1},
            "venus": {"sign": "Taurus", "house": 2},
            "mars": {"sign": "Leo", "house": 5}
        },
        "ascendant": {"sign": "Aries"},
        "aspects": [
            {"p1": "Sun", "p2": "Moon", "aspect": "Square"},
            {"p1": "Venus", "p2": "Mars", "aspect": "Trine"}
        ]
    }
    
    request = {
        "tool": "get_astrology_interpretation",
        "arguments": {
            "chart_data": chart_data,
            "focus": "personality"
        }
    }
    
    print("📋 Requisição:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    print("📊 Resultado esperado:")
    print("• Interpretação focada em personalidade")
    print("• Análise de planetas em signos")
    print("• Significado dos aspectos")
    print("• Insights astrológicos")
    print()

def demo_use_cases():
    """Mostra casos de uso práticos"""
    print("🎯 CASOS DE USO PRÁTICOS")
    print("=" * 40)
    
    use_cases = [
        {
            "title": "Consulta Astrológica Completa",
            "description": "Calcular mapa natal + trânsitos atuais + interpretação",
            "tools": ["calculate_natal_chart", "get_current_transits", "get_astrology_interpretation"]
        },
        {
            "title": "Análise de Relacionamento",
            "description": "Comparar mapas natais de duas pessoas",
            "tools": ["calculate_natal_chart", "generate_combined_svg_chart"]
        },
        {
            "title": "Previsão Astrológica",
            "description": "Verificar aspectos de trânsitos futuros ao natal",
            "tools": ["calculate_transits_to_natal", "get_astrology_interpretation"]
        },
        {
            "title": "Relatório Visual",
            "description": "Gerar gráficos para apresentação ou estudo",
            "tools": ["generate_svg_chart", "generate_combined_svg_chart"]
        },
        {
            "title": "Análise de Momento",
            "description": "Verificar a 'qualidade' astrológica de um momento",
            "tools": ["get_current_transits", "generate_svg_chart"]
        }
    ]
    
    for i, case in enumerate(use_cases, 1):
        print(f"{i}. {case['title']}")
        print(f"   📝 {case['description']}")
        print(f"   🔧 Ferramentas: {', '.join(case['tools'])}")
        print()

def main():
    """Executa todas as demonstrações"""
    print("🌟 DEMONSTRAÇÃO COMPLETA - SERVIDOR MCP DE ASTROLOGIA")
    print("=" * 60)
    print()
    print("Este servidor MCP permite integrar cálculos astrológicos")
    print("avançados em aplicações de IA, fornecendo 6 ferramentas")
    print("principais para análise astrológica completa.")
    print()
    
    # Executar todas as demos
    demo_natal_chart()
    demo_current_transits()
    demo_transits_to_natal()
    demo_svg_chart()
    demo_combined_svg()
    demo_interpretation()
    demo_use_cases()
    
    print("💡 PRÓXIMOS PASSOS")
    print("=" * 40)
    print("1. 📦 Instalar MCP: pip install mcp")
    print("2. 🚀 Iniciar API ToAMAO em localhost:8000")
    print("3. 🔧 Executar: python3 mcp-astrology-server.py")
    print("4. 🤖 Configurar cliente MCP (ex: Claude Desktop)")
    print("5. ✨ Usar ferramentas astrológicas em conversas!")
    print()
    print("🔗 Recursos:")
    print("• README-MCP-Astrology.md - Documentação completa")
    print("• claude-mcp-config.json - Configuração para Claude")
    print("• start-astrology-services.sh - Script de inicialização")
    print("• test-mcp-astrology.py - Testes automatizados")

if __name__ == "__main__":
    main()