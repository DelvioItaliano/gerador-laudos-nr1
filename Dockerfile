# Use a imagem oficial do n8n como base
FROM n8nio/n8n:latest

# Precisamos ser root para instalar pacotes
USER root

# Instala Python 3 e bibliotecas via APK (inclui reportlab pronto)
RUN apk update && apk add --no-cache \
    python3 py3-pip \
    py3-numpy py3-pandas py3-matplotlib py3-openpyxl \
    py3-reportlab \
    build-base \
 && ln -sf /usr/bin/python3 /usr/bin/python \
 && python3 -m pip install --no-cache-dir --upgrade pip

# Cria diretório e copia seu script
RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/

# Permissões
RUN chown -R node:node /scripts

# Volta para o usuário padrão
USER node


