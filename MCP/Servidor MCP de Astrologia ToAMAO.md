# Servidor MCP de Astrologia ToAMAO

Este é um servidor MCP (Model Context Protocol) que fornece interface para a API de astrologia ToAMAO, permitindo cálculos astrológicos avançados através de ferramentas de IA.

## Funcionalidades

### 🌟 Mapas Natais
- **calculate_natal_chart**: Calcula mapa natal completo com planetas, casas e aspectos
- Suporta diferentes sistemas de casas (Placidus, Koch, etc.)
- Inclui planetas principais, Chiron e Lilith
- Retorna aspectos detalhados entre planetas

### 🌙 Trânsitos
- **get_current_transits**: Obtém posições planetárias para qualquer data/hora
- **calculate_transits_to_natal**: Calcula aspectos entre trânsitos e mapa natal
- Útil para previsões e análise de períodos específicos

### 🎨 Gráficos SVG
- **generate_svg_chart**: Gera gráficos astrológicos visuais
  - Tipos: natal, trânsito ou combinado
  - Múltiplos temas visuais
  - Retorno em SVG direto ou base64
- **generate_combined_svg_chart**: Gráfico especializado natal + trânsitos
  - Visualização otimizada para aspectos entre mapas
  - Saída em SVG ou base64

### 🔮 Interpretação
- **get_astrology_interpretation**: Interpretação básica de dados astrológicos
- Focos: geral, personalidade, relacionamentos, carreira, espiritual

## Instalação

### 1. Instalar Dependências
```bash
pip3 install -r requirements-mcp.txt
```

### 2. Configurar API
Certifique-se de que a API ToAMAO esteja rodando:
```bash
cd ToAMAO
python3 main.py
# ou
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Configurar MCP
Adicione a configuração do servidor no seu cliente MCP:
```json
{
  "mcpServers": {
    "astrology": {
      "command": "python3",
      "args": ["/caminho/para/mcp-astrology-server.py"],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "API_KEY": "testapikey"
      }
    }
  }
}
```

### 4. Executar Servidor
```bash
python3 mcp-astrology-server.py
```

## Exemplos de Uso

### Calcular Mapa Natal
```json
{
  "name": "João Silva",
  "year": 1990,
  "month": 3,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "latitude": -23.5505,
  "longitude": -46.6333,
  "tz_str": "America/Sao_Paulo",
  "house_system": "placidus"
}
```

### Obter Trânsitos Atuais
```json
{
  "year": 2025,
  "month": 6,
  "day": 5,
  "hour": 12,
  "minute": 0,
  "latitude": -23.5505,
  "longitude": -46.6333,
  "tz_str": "America/Sao_Paulo",
  "name": "Trânsitos Hoje"
}
```

### Gerar Gráfico SVG
```json
{
  "natal_chart": {
    "name": "Mapa Exemplo",
    "year": 1990,
    "month": 3,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "latitude": -23.5505,
    "longitude": -46.6333,
    "tz_str": "America/Sao_Paulo"
  },
  "chart_type": "natal",
  "theme": "Kerykeion"
}
```

## Estrutura da API Original

O servidor MCP faz interface com os seguintes endpoints da API ToAMAO:

- `POST /api/v1/natal_chart` - Cálculo de mapa natal
- `POST /api/v1/current_transits` - Trânsitos atuais
- `POST /api/v1/transits_to_natal` - Aspectos trânsito-natal
- `POST /api/v1/svg_chart` - Gráficos SVG
- `POST /api/v1/svg_chart_base64` - Gráficos SVG em base64
- `POST /api/v1/svg_combined_chart` - Gráficos combinados
- `POST /api/v1/svg_combined_chart_base64` - Gráficos combinados em base64

## Configuração Avançada

### Variáveis de Ambiente
- `API_BASE_URL`: URL da API ToAMAO (padrão: http://localhost:8000)
- `API_KEY`: Chave de autenticação da API (padrão: testapikey)

### Sistemas de Casas Suportados
- placidus (padrão)
- koch
- regiomontanus
- campanus
- equal
- whole_sign

### Temas de Gráficos
- Kerykeion (padrão)
- Outros temas disponíveis na biblioteca Kerykeion

## Troubleshooting

### API não responde
1. Verifique se a API ToAMAO está rodando
2. Confirme a URL e porta corretas
3. Teste a API diretamente: `curl http://localhost:8000/`

### Erro de autenticação
1. Verifique a API_KEY
2. Confirme se a API está configurada para aceitar a chave

### Erro de cálculo astrológico
1. Verifique os dados de entrada (datas, coordenadas, fuso horário)
2. Confirme se as dependências da API estão instaladas (kerykeion, etc.)

## Contribuição

Para contribuir com o desenvolvimento:
1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## Licença

Este projeto segue a mesma licença do projeto ToAMAO original.