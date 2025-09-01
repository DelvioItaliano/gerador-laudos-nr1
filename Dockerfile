
FROM n8nio/n8n:latest

# Cache-bust para forçar rebuild quando necessário
ARG CACHE_BUST=1
RUN echo "CACHE_BUST=$CACHE_BUST"

# Precisamos ser root para instalar pacotes
USER root


# Python + libs via APK (inclui reportlab pronto)
RUN apk update && apk add --no-cache \
    python3 py3-pip \
    py3-numpy py3-pandas py3-matplotlib py3-openpyxl py3-reportlab \
    build-base ca-certificates \
 && update-ca-certificates \
 && ln -sf /usr/bin/python3 /usr/bin/python

# Scripts
RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/
RUN chown -R node:node /scripts

USER node




