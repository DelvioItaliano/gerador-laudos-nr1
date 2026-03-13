# API Flask - Geração de Laudos COPSOQ III - NR-1
# Empório do Líder

FROM python:3.11-slim

LABEL maintainer="Empório do Líder <contato@emporiodolider.com.br>"
LABEL description="API Flask para geração de laudos COPSOQ III - NR-1"
LABEL version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=api_laudo.py \
    FLASK_ENV=production \
    PORT=5000

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api_laudo.py .
COPY pipeline_copsoq_COM_AEP_FINAL.py .

RUN mkdir -p /home/n8n/scripts /tmp/laudos && \
    cp pipeline_copsoq_COM_AEP_FINAL.py /home/n8n/scripts/ && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /tmp/laudos /home/n8n

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "180", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "api_laudo:app"]
