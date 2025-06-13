-- Inicialização do Banco de Dados Astrotagiario
-- Estrutura para suportar usuários, cache e logs de execução

-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- === TABELAS DE USUÁRIOS ===

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT true,
    auto_reports BOOLEAN DEFAULT false,
    notification_preferences JSONB DEFAULT '{"email": true, "slack": false}',
    subscription_plan VARCHAR(50) DEFAULT 'free',
    last_login TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Tabela de perfis astrológicos dos usuários
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    birth_year INTEGER NOT NULL,
    birth_month INTEGER NOT NULL CHECK (birth_month >= 1 AND birth_month <= 12),
    birth_day INTEGER NOT NULL CHECK (birth_day >= 1 AND birth_day <= 31),
    birth_hour INTEGER NOT NULL CHECK (birth_hour >= 0 AND birth_hour <= 23),
    birth_minute INTEGER NOT NULL CHECK (birth_minute >= 0 AND birth_minute <= 59),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone VARCHAR(100) NOT NULL,
    house_system VARCHAR(50) DEFAULT 'placidus',
    birth_location VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- === TABELAS DE CACHE ===

-- Cache de mapas natais
CREATE TABLE IF NOT EXISTS natal_chart_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    chart_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days'),
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT NOW()
);

-- === TABELAS DE LOGS ===

-- Log de requisições da API
CREATE TABLE IF NOT EXISTS api_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_data JSONB,
    response_status INTEGER,
    response_time INTEGER, -- em milissegundos
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    error_message TEXT,
    execution_id UUID -- referência ao Kestra execution
);

-- Log de execuções do Kestra
CREATE TABLE IF NOT EXISTS kestra_executions (
    id UUID PRIMARY KEY,
    flow_id VARCHAR(255) NOT NULL,
    namespace VARCHAR(255) NOT NULL,
    execution_status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration INTEGER, -- em segundos
    inputs JSONB,
    outputs JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- === CONFIGURAÇÕES ===

-- Configurações do sistema
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255)
);

-- === ÍNDICES ===

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);
CREATE INDEX IF NOT EXISTS idx_natal_cache_key ON natal_chart_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_requests_endpoint ON api_requests(endpoint);
CREATE INDEX IF NOT EXISTS idx_kestra_executions_flow ON kestra_executions(flow_id);

-- === DADOS INICIAIS ===

-- Configurações padrão
INSERT INTO system_config (key, value, description) VALUES
('cache_ttl_natal', '{"days": 30}', 'TTL padrão para cache de mapas natais'),
('api_rate_limit', '{"requests_per_minute": 60}', 'Limite de requisições por minuto'),
('kestra_webhook_url', '{"url": "http://kestra:8080"}', 'URL do webhook do Kestra')
ON CONFLICT (key) DO NOTHING;

-- Usuários de exemplo
INSERT INTO users (id, email, name, auto_reports, subscription_plan) VALUES
('11111111-1111-1111-1111-111111111111', 'joao.victor@example.com', 'João Victor', true, 'premium'),
('22222222-2222-2222-2222-222222222222', 'maria.silva@example.com', 'Maria Silva', true, 'free')
ON CONFLICT (email) DO NOTHING;

-- Perfis astrológicos de exemplo
INSERT INTO user_profiles (user_id, birth_year, birth_month, birth_day, birth_hour, birth_minute, latitude, longitude, timezone, birth_location) VALUES
('11111111-1111-1111-1111-111111111111', 1997, 10, 13, 22, 0, -3.7172, -38.5247, 'America/Fortaleza', 'Fortaleza, CE'),
('22222222-2222-2222-2222-222222222222', 1990, 5, 15, 14, 30, -23.5505, -46.6333, 'America/Sao_Paulo', 'São Paulo, SP')
ON CONFLICT (user_id) DO NOTHING;

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Banco de dados Astrotagiario inicializado com sucesso!';
    RAISE NOTICE '📊 Tabelas criadas: users, user_profiles, caches, logs';
    RAISE NOTICE '🎯 Dados de exemplo inseridos para testes';
END $$;