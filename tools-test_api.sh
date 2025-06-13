#!/bin/bash

# Script de teste completo para a API Astrotagiario
# Testa todos os endpoints principais e valida respostas

set -euo pipefail

# Configurações
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-testapikey}"
VERBOSE="${VERBOSE:-false}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Funções utilitárias
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

# Função para fazer requisições HTTP
make_request() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    local expected_status="${4:-200}"
    
    ((TESTS_TOTAL++))
    
    if [[ -n "$data" ]]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            "$API_BASE_URL$endpoint" \
            -H "X-API-KEY: $API_KEY")
    fi
    
    # Separar corpo da resposta e status code
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)
    
    if [[ "$http_code" == "$expected_status" ]]; then
        ((TESTS_PASSED++))
        log "✅ PASS: $method $endpoint (HTTP $http_code)"
        echo "$response_body"
        return 0
    else
        ((TESTS_FAILED++))
        error "❌ FAIL: $method $endpoint (Expected $expected_status, got $http_code)"
        return 1
    fi
}

# Teste de health check
test_health() {
    log "🏥 Testing health check..."
    
    response=$(make_request "GET" "/health")
    if [[ $? -eq 0 ]]; then
        if echo "$response" | grep -q "healthy"; then
            log "✅ Health check returned 'healthy'"
        else
            error "⚠️ Health check didn't return expected 'healthy' message"
        fi
    fi
    echo
}

# Teste de mapa natal
test_natal_chart() {
    log "🌟 Testing natal chart calculation..."
    
    local test_data='{
        "name": "Test User API",
        "year": 1997,
        "month": 10,
        "day": 13,
        "hour": 22,
        "minute": 0,
        "latitude": -3.7172,
        "longitude": -38.5247,
        "tz_str": "America/Fortaleza",
        "house_system": "placidus"
    }'
    
    response=$(make_request "POST" "/api/v1/natal_chart" "$test_data")
    if [[ $? -eq 0 ]]; then
        # Verificar se há planetas suficientes
        planet_count=$(echo "$response" | jq '.planets | length')
        if [[ $planet_count -ge 10 ]]; then
            log "✅ Found $planet_count planets (expected ≥10)"
        else
            error "⚠️ Only found $planet_count planets (expected ≥10)"
        fi
    fi
    echo
}

# Teste de trânsitos diários
test_daily_transits() {
    log "📅 Testing daily transits..."
    
    local test_data='{
        "year": 2025,
        "month": 6,
        "day": 13
    }'
    
    response=$(make_request "POST" "/api/v1/transits/daily" "$test_data")
    if [[ $? -eq 0 ]]; then
        # Verificar se há aspectos
        aspect_count=$(echo "$response" | jq '.aspects | length')
        if [[ $aspect_count -gt 0 ]]; then
            log "✅ Found $aspect_count daily aspects"
        else
            error "⚠️ No daily aspects found"
        fi
    fi
    echo
}

# Teste de performance básico
test_performance() {
    log "⚡ Testing basic performance..."
    
    local test_data='{
        "name": "Performance Test",
        "year": 1990,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "latitude": -23.5505,
        "longitude": -46.6333,
        "tz_str": "America/Sao_Paulo"
    }'
    
    # Primeira chamada (cache miss)
    log "Testing cache miss performance..."
    start_time=$(date +%s.%N)
    response=$(make_request "POST" "/api/v1/natal_chart" "$test_data")
    end_time=$(date +%s.%N)
    cache_miss_time=$(echo "$end_time - $start_time" | bc)
    
    if [[ $? -eq 0 ]]; then
        log "✅ Cache miss took: ${cache_miss_time}s"
    fi
    
    # Segunda chamada (cache hit)
    log "Testing cache hit performance..."
    start_time=$(date +%s.%N)
    response=$(make_request "POST" "/api/v1/natal_chart" "$test_data")
    end_time=$(date +%s.%N)
    cache_hit_time=$(echo "$end_time - $start_time" | bc)
    
    if [[ $? -eq 0 ]]; then
        log "✅ Cache hit took: ${cache_hit_time}s"
    fi
    echo
}

# Sumário dos resultados
show_summary() {
    echo
    echo -e "${BLUE}=== TEST SUMMARY ===${NC}"
    echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"
    echo -e "${BLUE}📊 Total:  $TESTS_TOTAL${NC}"
    echo
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! API is working correctly.${NC}"
        exit 0
    else
        echo -e "${RED}💥 Some tests failed. Check the API configuration.${NC}"
        exit 1
    fi
}

# Função principal
main() {
    echo -e "${BLUE}🧪 Astrotagiario API Test Suite${NC}"
    echo -e "${BLUE}API Base URL: $API_BASE_URL${NC}"
    echo
    
    # Verificar se a API está acessível
    if ! curl -sf "$API_BASE_URL/health" >/dev/null; then
        error "❌ API is not accessible at $API_BASE_URL"
        exit 1
    fi
    
    log "🚀 Starting API tests..."
    echo
    
    # Executar todos os testes
    test_health
    test_natal_chart
    test_daily_transits
    test_performance
    
    # Mostrar sumário
    show_summary
}

# Verificar dependências
check_dependencies() {
    local deps=("curl" "jq" "bc")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Dependency '$dep' is not installed"
            exit 1
        fi
    done
}

# Verificar dependências e executar
check_dependencies
main "$@"