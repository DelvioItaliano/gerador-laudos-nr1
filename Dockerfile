# Use a imagem oficial do n8n como base
FROM n8nio/n8n:latest
# (opcional, fixe uma versão estável, ex.: n8nio/n8n:1.72.1)

# Precisamos ser root para instalar pacotes
USER root

# Instala Python e pip (slim) e limpa cache do apt
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# (opcional) garantir que "python" aponte para python3
RUN ln -s /usr/bin/python3 /usr/local/bin/python || true

# Instala libs Python
RUN python3 -m pip install --no-cache-dir matplotlib pandas openpyxl

# Cria diretório para scripts e copia seu arquivo
RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/

# Volta para o usuário padrão do n8n
USER node
