# Use a imagem oficial do n8n como base
FROM n8nio/n8n:latest

# Precisamos ser root para instalar pacotes
USER root

# Instala as dependências do sistema e do Python via APK
# 'build-base' e os pacotes '-dev' são necessários para compilar bibliotecas Python
RUN apk update && apk add --no-cache \
    python3 py3-pip \
    py3-numpy py3-pandas py3-matplotlib py3-openpyxl \
    build-base jpeg-dev zlib-dev

# Cria um link simbólico para que 'python' seja um alias para 'python3'
RUN ln -sf /usr/bin/python3 /usr/bin/python \
 && python3 -m pip install --no-cache-dir --upgrade pip

# Instala a biblioteca 'reportlab' usando pip
RUN pip3 install --no-cache-dir reportlab

# Cria diretório e copia seu script
RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/

# Permissões
RUN chown -R node:node /scripts

# Volta para o usuário padrão
USER node



