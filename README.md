# API de Geração de Laudos COPSOQ III - NR-1

API Flask para geração automática de laudos de avaliação de riscos psicossociais conforme NR-1 e NR-17.

**Desenvolvido por:** Empório do Líder  
**Versão:** 1.0.0  
**Data:** Novembro 2025

---

## 📋 Descrição

Esta API recebe dados de respostas do questionário COPSOQ III (Copenhagen Psychosocial Questionnaire) e gera automaticamente um laudo técnico em PDF com análise de riscos psicossociais, gráficos e recomendações.

---

## 🚀 Tecnologias

- **Python 3.11**
- **Flask 3.0** - Framework web
- **Gunicorn** - WSGI HTTP Server
- **Pandas** - Processamento de dados
- **Matplotlib** - Geração de gráficos
- **FPDF** - Geração de PDF
- **Docker** - Containerização

---

## 📡 Endpoints

### **POST /gerar-laudo**

Gera laudo PDF a partir das respostas do COPSOQ III.

**Request Body:**
```json
{
  "empresa": "Nome da Empresa",
  "respostas": [
    {
      "Carimbo de data/hora": "2025-11-06 10:00:00",
      "Empresa": "Empresa Teste",
      "Unidade": "Matriz",
      "Setor": "TI",
      "Cargo": "Analista",
      "Email": "teste@empresa.com",
      "Q1": "Às vezes",
      "Q2": "Raramente",
      ...
      "Q36": "Nunca/quase nunca"
    }
  ]
}
```

**Response:**
- **200 OK:** PDF do laudo (binary)
- **400 Bad Request:** Dados inválidos
- **500 Internal Server Error:** Erro ao gerar laudo

---

### **GET /health**

Health check do serviço.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-06T10:00:00",
  "python_version": "3.11.0",
  "script_exists": true,
  "script_path": "/home/n8n/scripts/pipeline_copsoq_COM_AEP_FINAL.py"
}
```

---

### **POST /test**

Endpoint de teste (retorna os dados recebidos).

**Response:**
```json
{
  "success": true,
  "message": "Dados recebidos com sucesso",
  "data_received": { ... },
  "timestamp": "2025-11-06T10:00:00"
}
```

---

## 🐳 Deploy com Docker

### **Build Local:**

```bash
docker build -t api-laudo-nr1 .
```

### **Run Local:**

```bash
docker run -d \
  --name api-laudo-nr1 \
  -p 5000:5000 \
  -v /tmp:/tmp \
  api-laudo-nr1
```

### **Testar:**

```bash
curl http://localhost:5000/health
```

---

## ☁️ Deploy no Northflank

Este repositório está configurado para deploy automático no Northflank.

**Configurações:**
- **Port:** 5000
- **Health Check:** `/health`
- **Resources:** 0.5 vCPU, 1 GB RAM (mínimo)
- **Timeout:** 180 segundos

---

## 🔧 Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `FLASK_ENV` | `production` | Ambiente Flask |
| `SCRIPT_PATH` | `/home/n8n/scripts/pipeline_copsoq_COM_AEP_FINAL.py` | Caminho do script Python |
| `MIN_RESPOSTAS` | `5` | Mínimo de respostas necessário |
| `TIMEOUT_SECONDS` | `120` | Timeout do script em segundos |

---

## 📊 Validações

A API valida automaticamente:
- ✅ Mínimo de 5 respostas
- ✅ Campos obrigatórios (empresa, respostas)
- ✅ Tipo de dados correto
- ✅ Colunas obrigatórias (Q1-Q36, Empresa, Unidade, Setor, Cargo, Email)

---

## 🔒 Segurança

- ✅ Container roda com usuário não-root
- ✅ Limpeza automática de arquivos temporários
- ✅ Timeout configurável para evitar processos travados
- ✅ Validação rigorosa de inputs

---

## 📝 Logs

A API gera logs detalhados em formato estruturado:

```
2025-11-06 10:00:00 - INFO - Recebida solicitação de laudo para empresa: Empresa Teste
2025-11-06 10:00:01 - INFO - Validação OK. Total de respostas: 20
2025-11-06 10:00:15 - INFO - PDF gerado com sucesso: /tmp/Laudo_COPSOQ_Empresa_Teste.pdf (245678 bytes)
```

---

## 🧪 Testes

### **Teste Manual:**

```bash
curl -X POST http://localhost:5000/gerar-laudo \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": "Empresa Teste",
    "respostas": [...]
  }' \
  --output laudo_teste.pdf
```

---

## 📦 Estrutura do Projeto

```
api-laudo-nr1/
├── Dockerfile                        # Configuração Docker
├── requirements.txt                  # Dependências Python
├── api_laudo.py                      # Código da API Flask
├── pipeline_copsoq_COM_AEP_FINAL.py  # Script de geração de laudo
├── .dockerignore                     # Arquivos ignorados no build
├── .gitignore                        # Arquivos ignorados no Git
└── README.md                         # Este arquivo
```

---

## 🤝 Integração com n8n

Esta API é projetada para ser chamada pelo n8n no workflow de geração de laudos.

**Exemplo de configuração no n8n:**

```json
{
  "method": "POST",
  "url": "https://api-laudo-nr1.northflank.app/gerar-laudo",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ ... }}",
  "options": {
    "timeout": 180000,
    "response": {
      "responseFormat": "file"
    }
  }
}
```

---

## 📄 Licença

© 2025 Empório do Líder. Todos os direitos reservados.

---

## 📞 Suporte

Para dúvidas ou problemas:
- **E-mail:** contato@emporiodolider.com.br
- **Website:** www.emporiodolider.com.br

---

**Desenvolvido com excelência para transformar ambientes de trabalho! 🚀**
