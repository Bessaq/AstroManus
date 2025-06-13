#!/usr/bin/env python3
"""
MCP Server para API de Astrologia ToAMAO
Este servidor MCP permite interagir com uma API completa de astrologia,
incluindo mapas natais, trânsitos e geração de gráficos SVG.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime
import httpx
from mcp.server import Server
from mcp.types import (
    CallToolResult,
    ListToolsResult, 
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)
from pydantic import BaseModel, Field

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("astrology-server")

# URL base da API de astrologia
API_BASE_URL = "http://localhost:8000"  # Ajuste conforme necessário
API_KEY = "testapikey"  # Chave de API padrão

# Modelo para dados de nascimento/evento
class NatalData(BaseModel):
    name: Optional[str] = None
    year: int
    month: int 
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    tz_str: str
    house_system: str = "placidus"

class TransitData(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    tz_str: str
    house_system: str = "placidus"
    name: Optional[str] = None

# Servidor MCP
server = Server("astrology-server")

async def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Faz requisições à API de astrologia com autenticação."""
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "POST":
            response = await client.post(url, json=data, headers=headers)
        else:
            response = await client.get(url, headers=headers)
            
        response.raise_for_status()
        
        # Para responses SVG
        if response.headers.get("content-type", "").startswith("image/svg"):
            return {"svg_content": response.text}
        
        return response.json()

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """Lista todas as ferramentas disponíveis."""
    
    tools = [
        Tool(
            name="calculate_natal_chart",
            description="Calcula um mapa natal completo com planetas, casas e aspectos",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome da pessoa"},
                    "year": {"type": "integer", "description": "Ano de nascimento"},
                    "month": {"type": "integer", "description": "Mês de nascimento (1-12)"},
                    "day": {"type": "integer", "description": "Dia de nascimento"},
                    "hour": {"type": "integer", "description": "Hora de nascimento (0-23)"},
                    "minute": {"type": "integer", "description": "Minuto de nascimento (0-59)"},
                    "latitude": {"type": "number", "description": "Latitude do local"},
                    "longitude": {"type": "number", "description": "Longitude do local"},
                    "tz_str": {"type": "string", "description": "Fuso horário (ex: America/Sao_Paulo)"},
                    "house_system": {"type": "string", "description": "Sistema de casas", "default": "placidus"}
                },
                "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
            }
        ),
        
        Tool(
            name="get_current_transits",
            description="Obtém as posições planetárias atuais ou para uma data específica",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "Ano"},
                    "month": {"type": "integer", "description": "Mês (1-12)"},
                    "day": {"type": "integer", "description": "Dia"},
                    "hour": {"type": "integer", "description": "Hora (0-23)"},
                    "minute": {"type": "integer", "description": "Minuto (0-59)"},
                    "latitude": {"type": "number", "description": "Latitude"},
                    "longitude": {"type": "number", "description": "Longitude"},
                    "tz_str": {"type": "string", "description": "Fuso horário"},
                    "house_system": {"type": "string", "description": "Sistema de casas", "default": "placidus"},
                    "name": {"type": "string", "description": "Nome opcional"}
                },
                "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
            }
        ),
        
        Tool(
            name="calculate_transits_to_natal",
            description="Calcula aspectos entre trânsitos atuais e um mapa natal",
            inputSchema={
                "type": "object",
                "properties": {
                    "natal_data": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "tz_str": {"type": "string"},
                            "house_system": {"type": "string", "default": "placidus"}
                        },
                        "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
                    },
                    "transit_data": {
                        "type": "object", 
                        "properties": {
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "tz_str": {"type": "string"},
                            "house_system": {"type": "string", "default": "placidus"},
                            "name": {"type": "string"}
                        },
                        "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
                    }
                },
                "required": ["natal_data", "transit_data"]
            }
        ),
        
        Tool(
            name="generate_svg_chart",
            description="Gera um gráfico astrológico em formato SVG",
            inputSchema={
                "type": "object",
                "properties": {
                    "natal_chart": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "tz_str": {"type": "string"},
                            "house_system": {"type": "string", "default": "placidus"}
                        },
                        "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
                    },
                    "transit_chart": {
                        "type": "object",
                        "properties": {
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "tz_str": {"type": "string"},
                            "house_system": {"type": "string", "default": "placidus"},
                            "name": {"type": "string"}
                        }
                    },
                    "chart_type": {
                        "type": "string",
                        "enum": ["natal", "transit", "combined"],
                        "description": "Tipo de gráfico"
                    },
                    "theme": {"type": "string", "description": "Tema visual", "default": "Kerykeion"},
                    "return_base64": {"type": "boolean", "description": "Retornar em base64", "default": False}
                },
                "required": ["natal_chart", "chart_type"]
            }
        ),
        
        Tool(
            name="generate_combined_svg_chart",
            description="Gera um gráfico SVG combinado especializado (natal + trânsitos)",
            inputSchema={
                "type": "object",
                "properties": {
                    "natal_chart": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "tz_str": {"type": "string"},
                            "house_system": {"type": "string", "default": "placidus"}
                        },
                        "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
                    },
                    "transit_chart": {
                        "type": "object",
                        "properties": {
                            "year": {"type": "integer"},
                            "month": {"type": "integer"},
                            "day": {"type": "integer"},
                            "hour": {"type": "integer"},
                            "minute": {"type": "integer"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "tz_str": {"type": "string"},
                            "house_system": {"type": "string", "default": "placidus"},
                            "name": {"type": "string"}
                        },
                        "required": ["year", "month", "day", "hour", "minute", "latitude", "longitude", "tz_str"]
                    },
                    "return_base64": {"type": "boolean", "description": "Retornar em base64", "default": False}
                },
                "required": ["natal_chart", "transit_chart"]
            }
        ),
        
        Tool(
            name="get_astrology_interpretation",
            description="Interpreta dados astrológicos fornecendo insights sobre planetas, casas e aspectos",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_data": {"type": "object", "description": "Dados do mapa natal"},
                    "focus": {
                        "type": "string",
                        "enum": ["general", "personality", "relationships", "career", "spiritual"],
                        "description": "Foco da interpretação",
                        "default": "general"
                    }
                },
                "required": ["chart_data"]
            }
        )
    ]
    
    return ListToolsResult(tools=tools)

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Executa as ferramentas do servidor."""
    
    try:
        if name == "calculate_natal_chart":
            result = await make_api_request("/api/v1/natal_chart", "POST", arguments)
            
            # Formatar resultado de forma mais legível
            planets_summary = []
            if "planets" in result:
                for planet_name, planet_data in result["planets"].items():
                    planets_summary.append(f"• {planet_data['name']}: {planet_data['sign']} na Casa {planet_data['house']}")
                    if planet_data['retrograde']:
                        planets_summary[-1] += " (Retrógrado)"
            
            aspects_summary = []
            if "aspects" in result:
                for aspect in result["aspects"][:10]:  # Limitar aos primeiros 10 aspectos
                    aspects_summary.append(f"• {aspect['p1_name']} {aspect['aspect']} {aspect['p2_name']} (orbe: {aspect['orbit']}°)")
            
            formatted_result = f"""
**Mapa Natal de {arguments.get('name', 'Pessoa')}**

**Planetas:**
{chr(10).join(planets_summary)}

**Ascendente:** {result.get('ascendant', {}).get('sign', 'N/A')}
**Meio do Céu:** {result.get('midheaven', {}).get('sign', 'N/A')}

**Principais Aspectos:**
{chr(10).join(aspects_summary)}

**Sistema de Casas:** {result.get('house_system', 'placidus')}
            """
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted_result)]
            )
            
        elif name == "get_current_transits":
            result = await make_api_request("/api/v1/current_transits", "POST", arguments)
            
            planets_summary = []
            if "planets" in result:
                for planet in result["planets"]:
                    planets_summary.append(f"• {planet['name']}: {planet['sign']} ({planet['position']:.2f}°)")
                    if planet['retrograde']:
                        planets_summary[-1] += " (Retrógrado)"
            
            formatted_result = f"""
**Trânsitos para {arguments.get('name', 'Data Especificada')}**
**Data:** {arguments['day']}/{arguments['month']}/{arguments['year']} às {arguments['hour']}:{arguments['minute']:02d}

**Posições Planetárias:**
{chr(10).join(planets_summary)}
            """
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted_result)]
            )
            
        elif name == "calculate_transits_to_natal":
            result = await make_api_request("/api/v1/transits_to_natal", "POST", arguments)
            
            aspects_summary = []
            if "aspects_to_natal" in result:
                for aspect in result["aspects_to_natal"]:
                    aspects_summary.append(f"• {aspect['transit_planet']} {aspect['aspect_name']} {aspect['natal_planet_or_point']} (orbe: {aspect['orbit']}°)")
            
            transit_planets = []
            if "transit_planets_positions" in result:
                for planet in result["transit_planets_positions"]:
                    transit_planets.append(f"• {planet['name']}: {planet['sign']}")
            
            formatted_result = f"""
**Trânsitos para Mapa Natal**

**Planetas em Trânsito:**
{chr(10).join(transit_planets)}

**Aspectos aos Planetas Natais:**
{chr(10).join(aspects_summary) if aspects_summary else "• Nenhum aspecto significativo encontrado"}
            """
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted_result)]
            )
            
        elif name == "generate_svg_chart":
            if arguments.get("return_base64", False):
                result = await make_api_request("/api/v1/svg_chart_base64", "POST", arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Gráfico SVG gerado em Base64:\n{result.get('data_uri', 'Erro ao gerar')}")]
                )
            else:
                result = await make_api_request("/api/v1/svg_chart", "POST", arguments)
                if "svg_content" in result:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Gráfico SVG gerado com sucesso!\n\n" + result["svg_content"][:500] + "...")]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Erro ao gerar gráfico SVG")]
                    )
                    
        elif name == "generate_combined_svg_chart":
            if arguments.get("return_base64", False):
                result = await make_api_request("/api/v1/svg_combined_chart_base64", "POST", arguments)
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Gráfico SVG combinado gerado em Base64:\n{result.get('data_uri', 'Erro ao gerar')}")]
                )
            else:
                result = await make_api_request("/api/v1/svg_combined_chart", "POST", arguments)
                if "svg_content" in result:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Gráfico SVG combinado gerado com sucesso!\n\n" + result["svg_content"][:500] + "...")]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Erro ao gerar gráfico SVG combinado")]
                    )
                    
        elif name == "get_astrology_interpretation":
            # Esta é uma função de interpretação local básica
            chart_data = arguments.get("chart_data", {})
            focus = arguments.get("focus", "general")
            
            interpretation = f"""
**Interpretação Astrológica - Foco: {focus.title()}**

Esta é uma interpretação básica dos dados astrológicos fornecidos.
Para uma análise mais detalhada, consulte um astrólogo profissional.

**Dados analisados:**
{json.dumps(chart_data, indent=2, ensure_ascii=False)[:1000]}...

**Nota:** Para interpretações mais profundas, use os dados do mapa natal 
calculado pelas outras ferramentas deste servidor.
            """
            
            return CallToolResult(
                content=[TextContent(type="text", text=interpretation)]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Ferramenta '{name}' não encontrada")]
            )
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Erro na API: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)]
        )
    except Exception as e:
        error_msg = f"Erro interno: {str(e)}"
        logger.error(error_msg)
        return CallToolResult(
            content=[TextContent(type="text", text=error_msg)]
        )

async def main():
    """Função principal para executar o servidor."""
    logger.info("Iniciando Servidor MCP de Astrologia...")
    logger.info(f"URL da API: {API_BASE_URL}")
    
    # Importar transport após verificar se mcp está disponível
    try:
        from mcp.server.stdio import stdio_server
    except ImportError:
        logger.error("MCP não está instalado. Execute: pip install mcp")
        return
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())