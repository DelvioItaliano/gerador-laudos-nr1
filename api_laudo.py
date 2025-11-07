"""
API Flask para Geração de Laudos COPSOQ III
Empório do Líder - NR-1

Autor: Manus AI
Data: 06 de Novembro de 2025
"""

from flask import Flask, request, send_file, jsonify
import pandas as pd
import os
import tempfile
import subprocess
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurações
SCRIPT_PATH = '/home/n8n/scripts/pipeline_copsoq_COM_AEP_FINAL.py'
PYTHON_EXECUTABLE = 'python3.11'
MIN_RESPOSTAS = 5
TIMEOUT_SECONDS = 120

@app.route('/gerar-laudo', methods=['POST'])
def gerar_laudo_endpoint():
    """
    Endpoint para gerar laudo COPSOQ III
    
    Body (JSON):
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
            },
            ...
        ]
    }
    
    Response:
    - 200: PDF do laudo (binary)
    - 400: Dados inválidos
    - 500: Erro ao gerar laudo
    """
    temp_excel = None
    pdf_path = None
    
    try:
        # Receber dados JSON
        data = request.get_json()
        logger.info(f"Recebida solicitação de laudo para empresa: {data.get('empresa', 'N/A')}")
        
        # Validar dados obrigatórios
        if not data:
            return jsonify({
                'success': False,
                'message': 'Corpo da requisição vazio ou inválido.'
            }), 400
        
        if 'respostas' not in data:
            return jsonify({
                'success': False,
                'message': 'Campo "respostas" é obrigatório.'
            }), 400
        
        if 'empresa' not in data:
            return jsonify({
                'success': False,
                'message': 'Campo "empresa" é obrigatório.'
            }), 400
        
        empresa = data['empresa']
        respostas = data['respostas']
        
        # Validar tipo de dados
        if not isinstance(respostas, list):
            return jsonify({
                'success': False,
                'message': 'Campo "respostas" deve ser uma lista.'
            }), 400
        
        # Validar mínimo de respostas
        if len(respostas) < MIN_RESPOSTAS:
            return jsonify({
                'success': False,
                'message': f'Mínimo de {MIN_RESPOSTAS} respostas necessário. Recebido: {len(respostas)}'
            }), 400
        
        logger.info(f"Validação OK. Total de respostas: {len(respostas)}")
        
        # Criar DataFrame a partir dos dados recebidos
        try:
            df = pd.DataFrame(respostas)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Erro ao processar respostas.',
                'error': str(e)
            }), 400
        
        # Validar colunas obrigatórias
        colunas_obrigatorias = ['Empresa', 'Unidade', 'Setor', 'Cargo', 'Email']
        colunas_obrigatorias += [f'Q{i}' for i in range(1, 37)]  # Q1 a Q36
        
        colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
        if colunas_faltantes:
            return jsonify({
                'success': False,
                'message': f'Colunas obrigatórias faltando: {", ".join(colunas_faltantes)}'
            }), 400
        
        # Criar arquivo Excel temporário
        temp_excel = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_excel.name, index=False)
        logger.info(f"Arquivo Excel temporário criado: {temp_excel.name}")
        
        # Executar script Python de geração do laudo
        logger.info(f"Executando script Python: {SCRIPT_PATH}")
        
        result = subprocess.run([
            PYTHON_EXECUTABLE,
            SCRIPT_PATH,
            temp_excel.name
        ], capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        
        # Verificar se houve erro
        if result.returncode != 0:
            logger.error(f"Erro ao executar script Python. Return code: {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            return jsonify({
                'success': False,
                'message': 'Erro ao gerar laudo.',
                'error': result.stderr,
                'stdout': result.stdout
            }), 500
        
        logger.info("Script Python executado com sucesso")
        logger.info(f"STDOUT: {result.stdout}")
        
        # Encontrar PDF gerado
        # O script gera o PDF com o nome: Laudo_COPSOQ_[empresa].pdf
        pdf_filename = f"Laudo_COPSOQ_{empresa.replace(' ', '_')}.pdf"
        pdf_path = os.path.join('/tmp', pdf_filename)
        
        # Tentar encontrar o PDF (pode ter nome ligeiramente diferente)
        if not os.path.exists(pdf_path):
            # Procurar por qualquer PDF gerado recentemente em /tmp
            import glob
            pdfs = glob.glob('/tmp/Laudo_COPSOQ_*.pdf')
            if pdfs:
                # Pegar o mais recente
                pdf_path = max(pdfs, key=os.path.getctime)
                logger.info(f"PDF encontrado: {pdf_path}")
            else:
                logger.error("PDF não foi gerado")
                return jsonify({
                    'success': False,
                    'message': 'PDF não foi gerado.',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }), 500
        
        # Verificar se arquivo existe e tem conteúdo
        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            logger.error(f"PDF inválido ou vazio: {pdf_path}")
            return jsonify({
                'success': False,
                'message': 'PDF gerado está vazio ou inválido.'
            }), 500
        
        logger.info(f"PDF gerado com sucesso: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
        
        # Retornar PDF
        download_name = f"Laudo_NR1_{empresa.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=download_name
        )
        
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout ao executar script Python ({TIMEOUT_SECONDS}s)")
        return jsonify({
            'success': False,
            'message': f'Timeout ao gerar laudo. Tempo limite: {TIMEOUT_SECONDS}s'
        }), 500
        
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor.',
            'error': str(e)
        }), 500
    
    finally:
        # Limpar arquivos temporários
        if temp_excel and os.path.exists(temp_excel.name):
            try:
                os.unlink(temp_excel.name)
                logger.info(f"Arquivo Excel temporário removido: {temp_excel.name}")
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporário: {e}")
        
        # Opcional: Remover PDF após envio (descomente se quiser)
        # if pdf_path and os.path.exists(pdf_path):
        #     try:
        #         os.unlink(pdf_path)
        #         logger.info(f"PDF removido: {pdf_path}")
        #     except Exception as e:
        #         logger.warning(f"Erro ao remover PDF: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    
    Response:
    {
        "status": "ok",
        "timestamp": "2025-11-06T10:00:00",
        "python_version": "3.11.0",
        "script_exists": true
    }
    """
    import sys
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'script_exists': os.path.exists(SCRIPT_PATH),
        'script_path': SCRIPT_PATH
    })


@app.route('/test', methods=['POST'])
def test_endpoint():
    """
    Endpoint de teste (retorna os dados recebidos)
    """
    data = request.get_json()
    return jsonify({
        'success': True,
        'message': 'Dados recebidos com sucesso',
        'data_received': data,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Verificar se script Python existe
    if not os.path.exists(SCRIPT_PATH):
        logger.warning(f"ATENÇÃO: Script Python não encontrado em {SCRIPT_PATH}")
        logger.warning("Atualize a variável SCRIPT_PATH no código")
    
    # Rodar servidor
    logger.info("Iniciando servidor Flask...")
    logger.info(f"Script Python: {SCRIPT_PATH}")
    logger.info(f"Python Executable: {PYTHON_EXECUTABLE}")
    logger.info(f"Mínimo de respostas: {MIN_RESPOSTAS}")
    logger.info(f"Timeout: {TIMEOUT_SECONDS}s")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
