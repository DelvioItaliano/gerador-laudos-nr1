FROM n8nio/n8n:latest

USER root
RUN apt update && apt install -y python3 python3-pip
RUN pip3 install matplotlib pandas openpyxl

RUN mkdir -p /scripts
COPY pipeline_forms_para_laudos_corrigido_final.py /scripts/

USER node