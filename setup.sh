#!/bin/bash

# Setup Script para Astrotagiario + Kestra
# Configuração completa do ambiente de desenvolvimento e produção

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções utilitárias
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado. Instale Docker primeiro."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        if ! docker compose version &> /dev/null; then
            error "Docker Compose não está instalado."
        fi
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
    
    log "✅ Docker encontrado: $(docker --version)"
    log "✅ Docker Compose encontrado: $($DOCKER_COMPOSE --version)"
}

# Criar diretórios necessários
create_directories() {
    log "📁 Criando diretórios necessários..."
    
    directories=(
        "output"
        "cache" 
        "logs"
        "temp"
        "backups"
        "nginx/ssl"
        "monitoring/grafana/dashboards"
        "monitoring/grafana/datasources"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log "   Created: $dir"
    done
}

# Construir imagem Docker do Astrotagiario
build_image() {
    log "🐳 Construindo imagem Docker do Astrotagiario..."
    
    if [[ ! -f "Dockerfile" ]]; then
        error "Dockerfile não encontrado. Execute este script do diretório raiz do projeto."
    fi
    
    docker build -t astrotagiario:latest . || error "Falha ao construir imagem Docker"
    log "✅ Imagem astrotagiario:latest construída com sucesso"
}

# Configurar variáveis de ambiente
setup_env() {
    log "⚙️ Configurando variáveis de ambiente..."
    
    if [[ ! -f ".env" ]]; then
        log "📄 Criando arquivo .env..."
        cat > .env << EOF
# Configurações do Astrotagiario
API_KEY_KERYKEION=testapikey
DATABASE_URL=postgresql://astro_user:astro_pass@astro_postgres:5432/astro_db
REDIS_URL=redis://astro_redis:6379/1

# Configurações do Kestra
KESTRA_URL=http://kestra:8080
KESTRA_UI_URL=http://localhost:8080

# Configurações de Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Configurações de Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Configurações de Ambiente
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
EOF
        log "✅ Arquivo .env criado. IMPORTANTE: Configure as variáveis de email e Slack!"
    else
        log "✅ Arquivo .env já existe"
    fi
}

# Configurar SSL auto-assinado para desenvolvimento
setup_ssl() {
    log "🔒 Configurando certificados SSL para desenvolvimento..."
    
    if [[ ! -f "nginx/ssl/astrotagiario.crt" ]]; then
        log "   Gerando certificado auto-assinado..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/astrotagiario.key \
            -out nginx/ssl/astrotagiario.crt \
            -subj "/C=BR/ST=CE/L=Fortaleza/O=Astrotagiario/CN=localhost" 2>/dev/null || true
        log "✅ Certificado SSL gerado"
    else
        log "✅ Certificado SSL já existe"
    fi
}

# Inicializar serviços
start_services() {
    log "🚀 Iniciando serviços..."
    
    # Verificar se há serviços rodando
    if $DOCKER_COMPOSE ps | grep -q "Up"; then
        warn "Alguns serviços já estão rodando. Reiniciando..."
        $DOCKER_COMPOSE down
    fi
    
    log "   Iniciando banco de dados primeiro..."
    $DOCKER_COMPOSE up -d postgresql astro_postgres redis astro_redis
    
    log "   Aguardando bancos de dados ficarem prontos..."
    sleep 30
    
    log "   Iniciando Kestra..."
    $DOCKER_COMPOSE up -d kestra
    
    log "   Aguardando Kestra ficar pronto..."
    sleep 45
    
    log "   Iniciando API do Astrotagiario..."
    $DOCKER_COMPOSE up -d astrotagiario-api
    
    log "   Iniciando serviços de monitoramento..."
    $DOCKER_COMPOSE up -d prometheus grafana
    
    log "   Iniciando proxy Nginx..."
    $DOCKER_COMPOSE up -d nginx
}

# Verificar saúde dos serviços
check_health() {
    log "🏥 Verificando saúde dos serviços..."
    
    services=(
        "http://localhost:8000/health|API Astrotagiario"
        "http://localhost:8080/health|Kestra UI"
        "http://localhost:9090/-/healthy|Prometheus"
        "http://localhost:3000/api/health|Grafana"
        "http://localhost/health|Nginx Proxy"
    )
    
    sleep 10  # Aguardar serviços iniciarem
    
    for service in "${services[@]}"; do
        IFS="|" read -r url name <<< "$service"
        log "   Verificando $name..."
        
        for i in {1..30}; do
            if curl -sf "$url" >/dev/null 2>&1; then
                log "   ✅ $name está saudável"
                break
            elif [[ $i -eq 30 ]]; then
                warn "   ⚠️ $name não respondeu após 30 tentativas"
            else
                sleep 2
            fi
        done
    done
}

# Exibir informações finais
show_info() {
    log "🎉 Setup concluído com sucesso!"
    echo
    echo -e "${BLUE}=== INFORMAÇÕES DE ACESSO ===${NC}"
    echo -e "${GREEN}🌟 API Astrotagiario:${NC}     http://localhost:8000"
    echo -e "${GREEN}📚 Documentação da API:${NC}   http://localhost:8000/docs"
    echo -e "${GREEN}🔧 Kestra UI:${NC}            http://localhost:8080"
    echo -e "${GREEN}📊 Grafana:${NC}              http://localhost:3000 (admin/astro123)"
    echo -e "${GREEN}📈 Prometheus:${NC}           http://localhost:9090"
    echo -e "${GREEN}🌐 Nginx Proxy:${NC}          http://localhost"
    echo
    echo -e "${BLUE}=== CREDENCIAIS PADRÃO ===${NC}"
    echo -e "${GREEN}API Key:${NC}                 testapikey"
    echo -e "${GREEN}Grafana:${NC}                 admin / astro123"
    echo
    echo -e "${BLUE}=== PRÓXIMOS PASSOS ===${NC}"
    echo -e "${YELLOW}1.${NC} Configure as variáveis de ambiente no arquivo .env"
    echo -e "${YELLOW}2.${NC} Importe os flows do Kestra em: http://localhost:8080/ui/flows"
    echo -e "${YELLOW}3.${NC} Execute testes: ./tools/test_api.sh"
    echo
    echo -e "${GREEN}🚀 Sistema pronto para uso!${NC}"
}

# Função principal
main() {
    if [[ $# -eq 0 ]]; then
        echo -e "${BLUE}=== ASTROTAGIARIO + KESTRA SETUP ===${NC}"
        echo "Executando setup completo..."
        check_docker
        create_directories
        setup_env
        setup_ssl
        build_image
        start_services
        check_health
        show_info
    else
        case $1 in
            "setup"|"install") 
                check_docker
                create_directories
                setup_env
                setup_ssl
                build_image
                start_services
                check_health
                show_info
                ;;
            "build") check_docker && build_image ;;
            "start") check_docker && start_services ;;
            "stop") $DOCKER_COMPOSE down ;;
            "health") check_health ;;
            *) 
                echo "Uso: $0 {setup|build|start|stop|health}"
                exit 1
                ;;
        esac
    fi
}

# Executar função principal
main "$@"