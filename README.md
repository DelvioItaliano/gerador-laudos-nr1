# Gerador de Laudos NR1

Projeto em Python que gera gráficos e laudos a partir de dados de Google Forms para atender exigências da NR1.

## Execução local

```bash
pip install -r requirements.txt
python pipeline_forms_para_laudos_corrigido_final.py
```

## Execução com Docker

```bash
docker build -t gerador-laudos-nr1 .
docker run --rm gerador-laudos-nr1
```
