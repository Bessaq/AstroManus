# Visualização SVG Combinada de Mapa Natal e Trânsitos

Este documento descreve a funcionalidade de visualização SVG combinada que mostra os aspectos entre um mapa natal e os planetas em trânsito na AstroAPI.

## Visão Geral

A funcionalidade de SVG combinado permite visualizar em um único gráfico:
- Planetas do mapa natal (círculos brancos)
- Planetas em trânsito (círculos azuis)
- Aspectos entre os planetas natais e os planetas em trânsito (linhas coloridas)

Esta visualização é especialmente útil para análises astrológicas que necessitam identificar rapidamente como os trânsitos planetários estão interagindo com o mapa natal.

## Como Usar

### Via API REST

A API oferece dois endpoints para geração de SVG combinado:

#### 1. Retorno direto do SVG

```
POST /api/v1/svg_combined_chart
```

**Corpo da requisição:**
```json
{
  "natal_chart": {
    "name": "João",
    "year": 1997,
    "month": 10,
    "day": 13,
    "hour": 22,
    "minute": 0,
    "latitude": -3.7172,
    "longitude": -38.5247,
    "tz_str": "America/Fortaleza",
    "house_system": "placidus"
  },
  "transit_chart": {
    "name": "Trânsitos 2025",
    "year": 2025,
    "month": 6,
    "day": 2,
    "hour": 12,
    "minute": 0,
    "latitude": -3.7172,
    "longitude": -38.5247,
    "tz_str": "America/Fortaleza",
    "house_system": "placidus"
  }
}
```

**Resposta:**
- Conteúdo SVG direto com Content-Type: image/svg+xml

#### 2. Retorno em formato Base64

```
POST /api/v1/svg_combined_chart_base64
```

**Corpo da requisição:** Mesmo formato do endpoint anterior

**Resposta:**
```json
{
  "svg_base64": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iODAwIj4...",
  "data_uri": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iODAwIj4..."
}
```

### Via Python

Para gerar o SVG combinado diretamente em Python:

```python
from kerykeion import AstrologicalSubject
from pathlib import Path
from app.utils.svg_combined_chart import generate_combined_chart

# Dados do mapa natal
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

# Dados dos trânsitos
transit_subject = AstrologicalSubject(
    name='Trânsitos',
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
output_dir = Path("/caminho/para/salvar")

# Gerar o SVG combinado
svg_path = generate_combined_chart(natal_subject, transit_subject, output_dir)
print(f"SVG combinado gerado: {svg_path}")
```

## Detalhes Técnicos

### Representação Visual

- **Planetas Natais:** Círculos brancos com borda preta
- **Planetas em Trânsito:** Círculos azul claro com borda azul
- **Aspectos:**
  - **Conjunção:** Linha vermelha sólida
  - **Oposição:** Linha azul sólida
  - **Trígono:** Linha verde tracejada
  - **Quadratura:** Linha magenta pontilhada
  - **Sextil:** Linha amarela tracejada
  - **Quincúncio:** Linha ciano pontilhada
  - Outros aspectos menores também são representados com cores distintas

### Orbes Utilizados

Os aspectos são calculados com os seguintes orbes máximos:
- Conjunção: 8°
- Oposição: 8°
- Trígono: 8°
- Quadratura: 7°
- Sextil: 6°
- Quincúncio: 5°
- Aspectos menores: 2-3°

## Exemplo

O exemplo abaixo mostra o mapa natal de João (13/10/1997, 22h, Fortaleza-CE) com os trânsitos de 02/06/2025:

![Exemplo de SVG Combinado](/tmp/astro_svg/João_com_transitos_Transitos_02_06_2025.svg)

## Limitações Atuais

- A biblioteca Kerykeion original não suporta nativamente a visualização de aspectos entre mapas natais e trânsitos
- Esta implementação usa uma solução personalizada com svgwrite para criar a visualização combinada
- Atualmente não há suporte para filtrar tipos específicos de aspectos na visualização

## Próximas Melhorias Planejadas

- Adicionar opção para filtrar aspectos por tipo
- Melhorar a legibilidade quando há muitos aspectos
- Adicionar informações detalhadas sobre cada aspecto ao passar o mouse (versão interativa)
- Opção para personalizar cores e estilos visuais
