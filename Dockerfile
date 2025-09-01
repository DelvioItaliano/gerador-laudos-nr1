# Use a imagem oficial do n8n como base
FROM n8nio/n8n:latest

# Define o usuário 'root' para instalar pacotes
USER root

# Instala as dependências do sistema usando 'apk'
RUN apk update && apk add --no-cache python3 py3-pip py3-numpy py3-pandas py3-matplotlib py3-openpyxl build-base

# Cria um link simbólico para que 'python' seja um alias para 'python3'
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Instala as dependências do seu projeto Python
RUN pip3 install --no-cache-dir reportlab

# Cria um diretório para os scripts
RUN mkdir -p /scripts

# Copia o seu script para o contêiner
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/

# Define as permissões corretas
RUN chown -R node:node /scripts

# Retorna para o usuário 'node'
USER node
