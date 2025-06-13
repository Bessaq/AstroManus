# Dockerfile para Astrotagiario - Otimizado para Kestra
FROM python:3.11-slim

# Metadados
LABEL maintainer="Astrotagiario Team"
LABEL description="API de Astrologia com Kerykeion para orquestração com Kestra"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    inkscape \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash astro

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependências adicionais para Kestra
COPY requirements-kestra.txt .
RUN pip install --no-cache-dir -r requirements-kestra.txt

# Copiar código do projeto
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/output /app/cache /app/logs /app/temp

# Dar permissões ao usuário astro
RUN chown -R astro:astro /app

# Mudar para usuário não-root
USER astro

# Expor porta para API (opcional)
EXPOSE 8000

# Comando padrão - pode ser sobrescrito pelo Kestra
CMD ["python", "-c", "print('🌟 Astrotagiario Docker Image Ready for Kestra!')"]