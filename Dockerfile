FROM n8nio/n8n:latest
USER root
RUN apk update && apk add --no-cache python3 py3-pip py3-numpy py3-pandas py3-matplotlib py3-openpyxl build-base \
 && ln -sf /usr/bin/python3 /usr/bin/python \
 && python3 -m pip install --no-cache-dir --upgrade pip
RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/
RUN chown -R node:node /scripts
USER node
