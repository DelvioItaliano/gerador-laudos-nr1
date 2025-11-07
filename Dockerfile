# Dockerfile otimizado para Northflank
# API Flask - Geração de Laudos COPSOQ III - NR-1
# Empório do Líder

FROM python:3.11-slim

# Metadados
LABEL maintainer="Empório do Líder <contato@emporiodolider.com.br>"
LABEL description="API Flask para geração de laudos COPSOQ III - NR-1"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=api_laudo.py \
    FLASK_ENV=production

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY api_laudo.py .
COPY pipeline_copsoq_COM_AEP_FINAL.py .

# Criar diretórios necessários
RUN mkdir -p /home/n8n/scripts /tmp/laudos
RUN cp pipeline_copsoq_COM_AEP_FINAL.py /home/n8n/scripts/

# Criar usuário não-root (segurança)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /tmp/laudos
USER appuser

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Comando para rodar (usando gunicorn para produção)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "180", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "api_laudo:app"]
