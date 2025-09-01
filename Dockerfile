# Imagem oficial do n8n (base Alpine)
FROM n8nio/n8n:latest
# (Opcional, fixe versão: n8nio/n8n:1.72.1)

# Precisamos ser root para instalar pacotes
USER root

# Instala Python 3 + pacotes Python via APK (mais rápido e estável no Alpine)
# Inclui toolchain básico caso precise compilar algo
RUN apk update \
 && apk add --no-cache \
      python3 py3-pip \
      py3-numpy py3-pandas py3-matplotlib py3-openpyxl \
      build-base \
 && ln -sf /usr/bin/python3 /usr/bin/python \
 && python3 -m pip install --no-cache-dir --upgrade pip

# Cria pasta e copia seu script
RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/

# Garante que o usuário do n8n tenha permissão de leitura/execução
RUN chown -R node:node /scripts

# Volta para o usuário padrão do n8n
USER node
