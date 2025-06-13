

## Endpoints da API Astrotagiario

### 1. Natal Chart (Mapa Natal)
- **Endpoint:** `/api/v1/natal_chart`
- **Método:** `POST`
- **Descrição:** Calcula e retorna os dados de um mapa natal.
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "name": "string",
  "year": 0,
  "month": 0,
  "day": 0,
  "hour": 0,
  "minute": 0,
  "latitude": 0,
  "longitude": 0,
  "tz_str": "string"
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/natal_chart" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"name\": \"Joao Victor\", \"year\": 1997, \"month\": 10, \"day\": 13, \"hour\": 22, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}"
```




### 2. SVG Combined Chart
- **Endpoint:** `/api/v1/svg_combined_chart`
- **Método:** `POST`
- **Descrição:** Gera um gráfico SVG combinado mostrando o mapa natal e os trânsitos com aspectos entre eles.
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "natal_chart": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  },
  "transit_chart": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  }
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/svg_combined_chart" \
-H "accept: image/svg+xml" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
--output combined_chart.svg \
-d "{\"natal_chart\": {\"name\": \"Joao Victor\", \"year\": 1997, \"month\": 10, \"day\": 13, \"hour\": 22, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}, \"transit_chart\": {\"name\": \"Transito Atual\", \"year\": 2025, \"month\": 6, \"day\": 8, \"hour\": 12, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}}"
```

### 3. SVG Combined Chart Base64
- **Endpoint:** `/api/v1/svg_combined_chart_base64`
- **Método:** `POST`
- **Descrição:** Gera um gráfico SVG combinado e retorna como string base64.
- **Parâmetros de Entrada (JSON Body):** (Mesmos do `/api/v1/svg_combined_chart`)
```json
{
  "natal_chart": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  },
  "transit_chart": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  }
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/svg_combined_chart_base64" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"natal_chart\": {\"name\": \"Joao Victor\", \"year\": 1997, \"month\": 10, \"day\": 13, \"hour\": 22, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}, \"transit_chart\": {\"name\": \"Transito Atual\", \"year\": 2025, \"month\": 6, \"day\": 8, \"hour\": 12, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}}"
```




### 4. Synastry
- **Endpoint:** `/api/v1/synastry`
- **Método:** `POST`
- **Descrição:** Calcula a sinastria (compatibilidade) entre dois mapas natais.
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "person1": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  },
  "person2": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  }
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/synastry" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"person1\": {\"name\": \"Joao Victor\", \"year\": 1997, \"month\": 10, \"day\": 13, \"hour\": 22, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}, \"person2\": {\"name\": \"Joao Paulo\", \"year\": 1995, \"month\": 6, \"day\": 13, \"hour\": 9, \"minute\": 30, \"latitude\": -3.6883, \"longitude\": -40.3586, \"tz_str\": \"America/Fortaleza\"}}"
```




### 5. Daily Transits
- **Endpoint:** `/api/v1/transits/daily`
- **Método:** `POST`
- **Descrição:** Retorna todos os aspectos planetários ativos para um dia específico.
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "year": 0,
  "month": 0,
  "day": 0
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/transits/daily" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"year\": 2025, \"month\": 6, \"day\": 8}"
```

### 6. Weekly Transits
- **Endpoint:** `/api/v1/transits/weekly`
- **Método:** `POST`
- **Descrição:** Entrega predição de 7 dias resumida (bom para alertas semanais).
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "year": 0,
  "month": 0,
  "day": 0
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/transits/weekly" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"year\": 2025, \"month\": 6, \"day\": 8}"
```




### 7. Moon Phase
- **Endpoint:** `/api/v1/moon_phase`
- **Método:** `POST`
- **Descrição:** Informa a fase da Lua para uma data específica.
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "year": 0,
  "month": 0,
  "day": 0
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/moon_phase" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"year\": 2025, \"month\": 6, \"day\": 8}"
```

### 8. Solar Return
- **Endpoint:** `/api/v1/solar_return`
- **Método:** `POST`
- **Descrição:** Calcula o próximo retorno solar e fornece destaques astrológicos.
- **Parâmetros de Entrada (JSON Body):**
```json
{
  "year": 0,
  "month": 0,
  "day": 0,
  "hour": 0,
  "minute": 0,
  "latitude": 0,
  "longitude": 0,
  "tz_str": "string"
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/solar_return" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"year\": 1997, \"month\": 10, \"day\": 13, \"hour\": 22, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}"
```




### 9. Synastry PDF Report
- **Endpoint:** `/api/v1/synastry-pdf-report`
- **Método:** `POST`
- **Descrição:** Gera relatório completo de sinastria em PDF.
- **Parâmetros de Entrada (JSON Body):** (Mesmos do `/api/v1/synastry`)
```json
{
  "person1": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  },
  "person2": {
    "name": "string",
    "year": 0,
    "month": 0,
    "day": 0,
    "hour": 0,
    "minute": 0,
    "latitude": 0,
    "longitude": 0,
    "tz_str": "string"
  }
}
```
- **Exemplo de Requisição `curl`:**
```bash
curl -X POST "http://localhost:8000/api/v1/synastry-pdf-report" \
-H "accept: application/json" \
-H "x-api-key: testapikey" \
-H "Content-Type: application/json" \
-d "{\"person1\": {\"name\": \"Joao Victor\", \"year\": 1997, \"month\": 10, \"day\": 13, \"hour\": 22, \"minute\": 0, \"latitude\": -3.7319, \"longitude\": -38.5267, \"tz_str\": \"America/Fortaleza\"}, \"person2\": {\"name\": \"Joao Paulo\", \"year\": 1995, \"month\": 6, \"day\": 13, \"hour\": 9, \"minute\": 30, \"latitude\": -3.6883, \"longitude\": -40.3586, \"tz_str\": \"America/Fortaleza\"}}"
```


