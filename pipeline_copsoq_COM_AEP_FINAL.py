# -*- coding: utf-8 -*-
import os
import re
import numpy as np
import pandas as pd

# usar backend sem display para salvar figuras
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fpdf import FPDF


# ------------------------------
# Função para normalizar textos
# ------------------------------
def safe_text(text: str) -> str:
    """Normaliza texto para latin-1 compatível com FPDF."""
    if not isinstance(text, str):
        text = str(text)

    # substitui caracteres problemáticos
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("“", "\"").replace("”", "\"")
    text = text.replace("…", "...")
    text = text.replace("’", "'")

    # remove qualquer coisa fora de latin-1
    return text.encode("latin-1", "replace").decode("latin-1")


# -------------------------------------
# Dicionário de interpretações COPSOQ III
# -------------------------------------
interpretacoes_copsoq = {
    "Demandas Quantitativas": {
        "Risco Baixo": "A carga de trabalho está bem distribuída e equilibrada. Os colaboradores conseguem completar suas tarefas dentro do tempo disponível.",
        "Risco Moderado": "Há momentos de acúmulo de trabalho que podem gerar pressão. Recomenda-se revisar a distribuição de tarefas e prazos.",
        "Risco Elevado": "Sobrecarga significativa de trabalho. Risco elevado de estresse e esgotamento. Medidas urgentes de redistribuição de demandas são necessárias."
    },
    "Ritmo de Trabalho": {
        "Risco Baixo": "O ritmo de trabalho é adequado e permite aos colaboradores trabalharem de forma sustentável.",
        "Risco Moderado": "O ritmo de trabalho é acelerado em alguns momentos. Atenção para evitar fadiga crônica.",
        "Risco Elevado": "Ritmo de trabalho excessivamente acelerado. Alto risco de burnout. Necessário revisar processos e prazos."
    },
    "Demandas Emocionais": {
        "Risco Baixo": "As interações no trabalho exigem pouca regulação emocional, sendo um ambiente emocionalmente estável.",
        "Risco Moderado": "Há uma exigência moderada de envolvimento emocional, o que pode ser desgastante para alguns colaboradores.",
        "Risco Elevado": "Alta exigência de envolvimento emocional no trabalho. Risco de exaustão emocional. Recomenda-se suporte e treinamento."
    },
    "Influência no Trabalho": {
        "Desfavorável": "Os colaboradores sentem que têm pouca ou nenhuma autonomia sobre seu trabalho, o que pode levar à desmotivação.",
        "Intermediário": "A autonomia é parcial. Existem oportunidades para aumentar a participação dos colaboradores nas decisões.",
        "Favorável": "Os colaboradores percebem ter boa autonomia e controle sobre suas tarefas, um fator protetivo importante."
    },
    "Possibilidades de Desenvolvimento": {
        "Desfavorável": "Faltam oportunidades de aprendizado e desenvolvimento de novas habilidades, gerando estagnação.",
        "Intermediário": "As oportunidades de desenvolvimento são pontuais. É possível ampliar programas de capacitação.",
        "Favorável": "A empresa oferece um ambiente rico em oportunidades de aprendizado e crescimento profissional."
    },
    "Significado do Trabalho": {
        "Desfavorável": "Os colaboradores não veem propósito ou significado em seu trabalho, o que afeta o engajamento.",
        "Intermediário": "O senso de propósito é moderado. Ações de comunicação sobre o impacto do trabalho podem ajudar.",
        "Favorável": "Os colaboradores sentem que seu trabalho é importante e significativo, fortalecendo a motivação."
    },
    "Reconhecimento": {
        "Desfavorável": "Falta de valorização e reconhecimento no trabalho, o que pode gerar desmotivação e alta rotatividade.",
        "Intermediário": "O reconhecimento é pontual, mas sem consistência. É necessário fortalecer a cultura de valorização.",
        "Favorável": "Os colaboradores se sentem valorizados e reconhecidos, gerando engajamento e pertencimento."
    },
    "Qualidade da Liderança": {
        "Desfavorável": "A liderança é percebida como pouco eficaz, com falhas no planejamento, comunicação e suporte.",
        "Intermediário": "A liderança apresenta pontos fortes e fracos. Recomenda-se treinamento em gestão de pessoas.",
        "Favorável": "As lideranças são percebidas como competentes, justas e inspiradoras, sendo um fator protetivo."
    },
    "Suporte Social do Supervisor": {
        "Desfavorável": "Os colaboradores não percebem apoio adequado de suas lideranças diretas, afetando o clima e o engajamento.",
        "Intermediário": "O suporte da liderança é parcial, porém ainda aquém do ideal para um ambiente de confiança.",
        "Favorável": "As lideranças são percebidas como acolhedoras e presentes, contribuindo para reduzir riscos psicossociais."
    },
    "Suporte Social dos Colegas": {
        "Desfavorável": "O ambiente entre colegas é marcado por falta de cooperação e suporte, o que pode gerar isolamento.",
        "Intermediário": "A colaboração entre colegas existe, mas pode ser aprimorada para fortalecer o espírito de equipe.",
        "Favorável": "Existe um forte senso de comunidade e apoio mútuo entre os colegas, um fator de proteção crucial."
    },
    "Justiça e Respeito": {
        "Desfavorável": "Há percepção de injustiça ou desrespeito no tratamento dos colaboradores, gerando um clima de desconfiança.",
        "Intermediário": "As práticas de gestão são percebidas como justas na maior parte do tempo, mas há espaço para melhorias.",
        "Favorável": "Os colaboradores sentem que são tratados com justiça e respeito, promovendo um ambiente de trabalho ético."
    },
    "Comunidade Social no Trabalho": {
        "Desfavorável": "O ambiente de trabalho apresenta sinais de conflito, desconfiança ou isolamento social.",
        "Intermediário": "O clima social tem pontos positivos e negativos, requerendo ajustes em cultura e comunicação.",
        "Favorável": "O clima social é saudável, colaborativo e estimulante, fortalecendo o bem-estar e o desempenho."
    },
    "Conflito Trabalho-Família": {
        "Risco Baixo": "O trabalho interfere pouco na vida pessoal dos colaboradores, permitindo um bom equilíbrio.",
        "Risco Moderado": "O trabalho ocasionalmente interfere na vida pessoal, gerando necessidade de atenção ao equilíbrio.",
        "Risco Elevado": "A interferência do trabalho na vida pessoal é alta, com risco de estresse e problemas familiares."
    },
    "Insegurança no Trabalho": {
        "Risco Baixo": "Os colaboradores sentem-se seguros em relação à estabilidade de seus empregos.",
        "Risco Moderado": "Existe alguma preocupação com a segurança no emprego, o que pode gerar ansiedade.",
        "Risco Elevado": "A insegurança em relação ao futuro no trabalho é alta, sendo um fator de estresse significativo."
    },
    "Estresse": {
        "Risco Baixo": "Os colaboradores relatam baixos níveis de estresse e tensão.",
        "Risco Moderado": "Há sinais de estresse que merecem atenção para evitar o agravamento.",
        "Risco Elevado": "Níveis de estresse elevados, indicando necessidade de intervenções para promover o bem-estar."
    },
    "Burnout": {
        "Risco Baixo": "Os colaboradores demonstram baixos níveis de exaustão física e emocional.",
        "Risco Moderado": "Sinais de esgotamento estão presentes e devem ser monitorados para prevenir o burnout.",
        "Risco Elevado": "Sinais claros de burnout, como exaustão e distanciamento emocional. Ações urgentes são necessárias."
    },
    "Sintomas Depressivos": {
        "Risco Baixo": "Os colaboradores relatam poucos ou nenhuns sintomas de desânimo ou perda de interesse.",
        "Risco Moderado": "Presença de sintomas depressivos leves a moderados, indicando necessidade de apoio.",
        "Risco Elevado": "Sintomas depressivos significativos são relatados, sendo crucial oferecer suporte psicológico e organizacional."
    }
}


# ------------------------------
# Classe do PDF
# ------------------------------
class LaudoNR1(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        # Margem de 25mm garante que o texto não invada o rodapé
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", x=10, y=8, w=25)
        self.set_font("Arial", "B", 14)
        self.set_xy(0, 15)
        self.cell(0, 8, safe_text("Sua Consultoria de Gestão Estratégica de Pessoas"), align="C")
        self.set_draw_color(50, 50, 50)
        self.line(10, 35, 200, 35)
        self.set_y(40)

    def footer(self):
        self.set_y(-22)
        self.set_draw_color(50, 50, 50)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_y(-17)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, safe_text("Emporio do Lider - Gestao de Pessoas e Treinamento"), ln=1, align="C")
        self.cell(0, 5, safe_text("CNPJ: 31.505.935/0001-53"), ln=1, align="C")
        self.cell(0, 5, safe_text("Telefone: (11) 97238-5938 | Site: www.emporiodolider.com.br"), align="C")

    def add_title(self, title):
        self.set_fill_color(220, 220, 220)
        self.set_draw_color(180, 180, 180)
        self.set_font("Arial", "B", 16)
        self.cell(190, 12, safe_text(title), border=1, ln=1, align="C", fill=True)
        self.ln(6)

    def add_section_title(self, section):
        self.ln(4)
        self.set_fill_color(220, 220, 220)
        self.set_draw_color(180, 180, 180)
        self.set_font("Arial", "B", 12)
        self.cell(190, 10, safe_text(section), ln=True, border=1, align="L", fill=True)
        self.ln(2)

    def add_paragraph(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6.5, safe_text(text))
        self.ln(1)
    def add_recomendacoes(self, texto):
        """
        Adiciona recomendações com formatação especial:
        - [CAIXA]texto[/CAIXA] = Texto em caixa cinza
        - [NEGRITO]texto[/NEGRITO] = Texto em negrito
        """
        linhas = texto.split('\n')
        
        for linha in linhas:
            # Processar caixas cinza
            if '[CAIXA]' in linha and '[/CAIXA]' in linha:
                # Extrair texto da caixa
                inicio = linha.find('[CAIXA]') + 7
                fim = linha.find('[/CAIXA]')
                texto_caixa = linha[inicio:fim]
                
                # Desenhar caixa cinza
                self.set_fill_color(220, 220, 220)  # Cinza claro
                self.set_font('Arial', 'B', 12)
                x_atual = self.get_x()
                y_atual = self.get_y()
                
                # Calcular largura da página
                largura_util = self.w - self.l_margin - self.r_margin
                
                # Desenhar retângulo cinza
                self.rect(x_atual, y_atual, largura_util, 8, 'F')
                
                # Escrever texto sobre o retângulo
                self.cell(largura_util, 8, safe_text(texto_caixa), border=0, align='L')
                self.ln(10)
                
            # Processar negrito
            elif '[NEGRITO]' in linha and '[/NEGRITO]' in linha:
                # Extrair texto em negrito
                inicio = linha.find('[NEGRITO]') + 9
                fim = linha.find('[/NEGRITO]')
                texto_negrito = linha[inicio:fim]
                
                # Escrever em negrito
                self.set_font('Arial', 'B', 11)
                self.multi_cell(0, 6.5, safe_text(texto_negrito))
                
            # Linha normal
            elif linha.strip():
                self.set_font('Arial', '', 11)
                self.multi_cell(0, 6.5, safe_text(linha))
            else:
                # Linha vazia
                self.ln(3)
        
        self.ln(1)
    


    def add_table_metodologia(self):
        self.set_font('Arial', 'B', 11)
        self.cell(60, 8, safe_text('Domínio COPSOQ III'), border=1, align='C')
        self.cell(100, 8, safe_text('Dimensões Avaliadas'), border=1, align='C')
        self.cell(30, 8, safe_text('Nº Itens'), border=1, align='C')
        self.ln()
        self.set_font('Arial', '', 10)
        linhas = [
            ('Demandas no Trabalho', 'Quantitativas, Ritmo, Emocionais', '6'),
            ('Organização e Conteúdo', 'Influência, Desenvolvimento, Significado', '6'),
            ('Relações e Liderança', 'Reconhecimento, Liderança, Suporte', '10'),
            ('Interface Trabalho-Indivíduo', 'Conflito Trabalho-Família, Insegurança', '4'),
            ('Valores Organizacionais', 'Justiça, Respeito, Comunidade', '4'),
            ('Indicadores de Saúde', 'Estresse, Burnout, Sintomas Depressivos', '6')
        ]
        for dominio, dimensoes, itens in linhas:
            self.cell(60, 8, safe_text(dominio), border=1)
            self.cell(100, 8, safe_text(dimensoes), border=1)
            self.cell(30, 8, safe_text(itens), border=1, align='C')
            self.ln()
        self.ln(3)

    def add_table_resultados(self, medias, classificacoes):
        self.set_font('Arial', 'B', 11)
        self.cell(80, 8, safe_text('Dimensão Avaliada'), border=1, align='C')
        self.cell(40, 8, safe_text('Resultado (0-100)'), border=1, align='C')
        self.cell(70, 8, safe_text('Classificação'), border=1, align='C')
        self.ln()
        self.set_font('Arial', '', 10)
        for dim, media in medias.items():
            classificacao = classificacoes.get(dim, {}).get("risco", "-")
            self.cell(80, 8, safe_text(dim), border=1)
            self.cell(40, 8, safe_text(f"{media:.1f}"), border=1, align='C')
            self.cell(70, 8, safe_text(classificacao), border=1, align='C')
            self.ln()
        self.ln(4)

    def add_table_referencias(self):
        self.set_font("Arial", "B", 10)
        self.cell(65, 8, safe_text("Dimensão"), border=1, align='C')
        self.cell(25, 8, safe_text("Tipo"), border=1, align='C')
        self.cell(30, 8, safe_text("Favorável"), border=1, align='C')
        self.cell(30, 8, safe_text("Intermediário"), border=1, align='C')
        self.cell(40, 8, safe_text("Desfavorável"), border=1, align='C', ln=True)

        self.set_font("Arial", "", 8)
        referencia = {
            "Exposição": ("0-33", "34-66", "67-100"),
            "Recurso": ("67-100", "34-66", "0-33"),
            "Resultado": ("0-33", "34-66", "67-100")
        }
        
        dimensoes_tipos = {
            "Demandas Quantitativas": "Exposição", "Ritmo de Trabalho": "Exposição", "Demandas Emocionais": "Exposição",
            "Conflito Trabalho-Família": "Exposição", "Insegurança no Trabalho": "Exposição",
            "Influência no Trabalho": "Recurso", "Possibilidades de Desenvolvimento": "Recurso", "Significado do Trabalho": "Recurso",
            "Reconhecimento": "Recurso", "Qualidade da Liderança": "Recurso", "Suporte Social do Supervisor": "Recurso",
            "Suporte Social dos Colegas": "Recurso", "Justiça e Respeito": "Recurso", "Comunidade Social no Trabalho": "Recurso",
            "Estresse": "Resultado", "Burnout": "Resultado", "Sintomas Depressivos": "Resultado"
        }

        for dim, tipo in dimensoes_tipos.items():
            fav, inter, desfav = referencia[tipo]
            self.cell(65, 7, safe_text(dim), border=1)
            self.cell(25, 7, safe_text(tipo), border=1, align='C')
            self.cell(30, 7, safe_text(fav), border=1, align='C')
            self.cell(30, 7, safe_text(inter), border=1, align='C')
            self.cell(40, 7, safe_text(desfav), border=1, align='C')
            self.ln()
        self.ln(3)

    def add_interpretacao(self, classificacoes):
        self.set_font("Arial", "", 10)
        for dimensao, classif in classificacoes.items():
            risco = classif.get("risco", "Sem classificação")
            self.set_font("Arial", "B", 10)
            self.cell(0, 6.5, safe_text(f"{dimensao} - {risco}"), ln=True)
            self.set_font("Arial", "", 10)
            texto = interpretacoes_copsoq.get(dimensao, {}).get(risco, "Sem interpretação disponível.")
            self.multi_cell(0, 6.5, safe_text(texto))
            self.ln(1)

    def add_plano_acao(self, plano_acao_dados=None):
        # Adiciona página em orientação paisagem para o Plano de Ação
        self.add_page(orientation='L')  # 'L' = Landscape (paisagem)
        
        self.add_section_title("6. Plano de Ação – Medidas Preventivas e Corretivas (NR-1, subitem 1.5.5.2.2)")
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, safe_text(
            "Em conformidade com a NR-1, subitem 1.5.5.2.2, este Plano de Ação apresenta as medidas preventivas "
            "e corretivas relacionadas aos riscos psicossociais identificados. "
            "Cada ação definida contém responsável, prazo de execução e status de acompanhamento, compondo assim "
            "o Inventário de Riscos e o Plano de Ação do PGR (Programa de Gerenciamento de Riscos).\n\n"
            "O cronograma aqui estabelecido não é apenas informativo, mas representa os compromissos formais de gestão "
            "assumidos pela empresa, devendo ser implementados e monitorados periodicamente. "
            "Sua execução e atualização contínua são fundamentais para assegurar a conformidade legal, "
            "reduzir riscos ocupacionais e promover um ambiente de trabalho saudável e produtivo."
        ))
        self.ln(3)
        
        # Se não houver dados dinâmicos, usar tabela estática (fallback)
        if plano_acao_dados is None or len(plano_acao_dados) == 0:
            self.set_font('Arial', '', 10)
            self.multi_cell(0, 6, safe_text(
                "Nenhuma ação prioritária identificada. Todas as dimensões estão em níveis favoráveis."
            ))
            self.ln(2)
            return
        
        # Tabela dinâmica com dados reais - LARGURAS AJUSTADAS PARA PAISAGEM
        self.set_font('Arial', 'B', 9)
        headers = ["Prior.", "Dimensão", "Ação Específica", "Responsável", "Prazo", "Indicador de Sucesso", "Status"]
        # Largura total disponível em paisagem: ~277mm (297 - 20 de margens)
        widths = [15, 40, 85, 30, 25, 60, 22]
        aligns = ['C', 'L', 'L', 'C', 'C', 'L', 'C']
        
        # Cabeçalho da tabela
        for i, h in enumerate(headers):
            self.cell(widths[i], 8, safe_text(h), border=1, align='C')
        self.ln()
        
        self.set_font('Arial', '', 9)
        for acao in plano_acao_dados:
            y_before = self.get_y()
            
            # Prioridade
            self.cell(widths[0], 8, safe_text(acao['prioridade']), border=1, align=aligns[0])
            
            # Dimensão com pontuação
            x_after = self.get_x()
            dimensao_texto = f"{acao['dimensao']} ({acao['pontuacao']:.1f})"
            self.multi_cell(widths[1], 8, safe_text(dimensao_texto), border=1, align=aligns[1])
            y_after_dim = self.get_y()
            
            # Ação
            self.set_xy(x_after + widths[1], y_before)
            self.multi_cell(widths[2], 8, safe_text(acao['acao']), border=1, align=aligns[2])
            y_after_acao = self.get_y()
            
            # Responsável
            self.set_xy(x_after + widths[1] + widths[2], y_before)
            self.multi_cell(widths[3], 8, safe_text(acao['responsavel']), border=1, align=aligns[3])
            y_after_resp = self.get_y()
            
            # Prazo
            self.set_xy(x_after + widths[1] + widths[2] + widths[3], y_before)
            prazo_texto = f"{acao['prazo_dias']} dias\n{acao['data_conclusao']}"
            self.multi_cell(widths[4], 8, safe_text(prazo_texto), border=1, align=aligns[4])
            y_after_prazo = self.get_y()
            
            # Indicador
            self.set_xy(x_after + widths[1] + widths[2] + widths[3] + widths[4], y_before)
            self.multi_cell(widths[5], 8, safe_text(acao['indicador']), border=1, align=aligns[5])
            y_after_ind = self.get_y()
            
            # Calcular altura máxima
            max_y = max(y_after_dim, y_after_acao, y_after_resp, y_after_prazo, y_after_ind)
            height = max_y - y_before
            
            # Status
            self.set_xy(x_after + widths[1] + widths[2] + widths[3] + widths[4] + widths[5], y_before)
            self.cell(widths[6], height, safe_text(acao['status']), border=1, align=aligns[6])
            
            self.set_y(max_y)
            self.ln(0)
        
        self.ln(2)


    def add_assinatura(self):
        self.ln(18)
        y = self.get_y()
        self.set_draw_color(0, 0, 0)
        self.line(60, y, 150, y)
        self.ln(4)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, safe_text("Responsável Técnico: Eloise Tancredi Nicoletti"), ln=True, align="C")
        self.set_font("Arial", "I", 6)
        self.cell(0, 5, safe_text("Terapeuta em PNL e Especialista em Inteligência Emocional pela ABPS – Associação Brasileira de Psicodrama e Sociodrama"), ln=True, align="C")
        self.set_font("Arial", "", 8)
        self.cell(0, 5, safe_text("CPF: 142.554.168-26"), ln=True, align="C")

# Função para gerar recomendações personalizadas baseadas nos resultados

# Função para gerar Plano de Ação Dinâmico baseado nos resultados

from datetime import datetime, timedelta

def gerar_plano_acao_dinamico(medias_dimensoes, num_trabalhadores=20):
    """
    Gera plano de ação dinâmico baseado nos resultados do COPSOQ III
    
    Args:
        medias_dimensoes: dict com as médias de cada dimensão
        num_trabalhadores: número de trabalhadores da empresa
    
    Returns:
        list de dicts com as ações do plano
    """
    
    # Mapeamento de dimensões para ações específicas
    acoes_db = {
        "Demandas Quantitativas": [
            {
                "acao": "Realizar diagnóstico de carga de trabalho por setor",
                "responsavel": "RH",
                "prazo_dias": 30,
                "indicador": "Relatório de diagnóstico concluído",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar pausas programadas conforme NR-17",
                "responsavel": "RH/Liderança",
                "prazo_dias": 60,
                "indicador": "100% dos setores com pausas implementadas",
                "prioridade": "ALTA"
            },
            {
                "acao": "Revisar distribuição de tarefas entre equipes",
                "responsavel": "Gestão",
                "prazo_dias": 90,
                "indicador": "Plano de redistribuição aprovado e em execução",
                "prioridade": "MÉDIA"
            }
        ],
        "Ritmo de Trabalho": [
            {
                "acao": "Identificar períodos de maior pressão temporal",
                "responsavel": "RH/Gestão",
                "prazo_dias": 30,
                "indicador": "Mapeamento de picos de demanda concluído",
                "prioridade": "ALTA"
            },
            {
                "acao": "Revisar prazos de projetos críticos",
                "responsavel": "Gestão",
                "prazo_dias": 60,
                "indicador": "80% dos prazos revisados e ajustados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar ginástica laboral e pausas ativas",
                "responsavel": "SESMT/RH",
                "prazo_dias": 90,
                "indicador": "Programa de ginástica laboral em funcionamento",
                "prioridade": "MÉDIA"
            }
        ],
        "Demandas Emocionais": [
            {
                "acao": "Oferecer treinamento em inteligência emocional",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "80% dos colaboradores treinados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Criar protocolo de suporte emocional",
                "responsavel": "SESMT/RH",
                "prazo_dias": 30,
                "indicador": "Protocolo documentado e divulgado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Disponibilizar apoio psicológico",
                "responsavel": "RH",
                "prazo_dias": 90,
                "indicador": "Serviço de apoio psicológico contratado",
                "prioridade": "MÉDIA"
            }
        ],
        "Influência no Trabalho": [
            {
                "acao": "Implementar metodologia OKR para alinhamento de metas",
                "responsavel": "Gestão",
                "prazo_dias": 90,
                "indicador": "OKRs definidos para todas as áreas",
                "prioridade": "MÉDIA"
            },
            {
                "acao": "Criar canais de participação nas decisões",
                "responsavel": "Liderança",
                "prazo_dias": 60,
                "indicador": "Canais de participação implementados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Aumentar autonomia dos colaboradores",
                "responsavel": "Liderança",
                "prazo_dias": 90,
                "indicador": "Pesquisa de autonomia com melhoria de 20%",
                "prioridade": "MÉDIA"
            }
        ],
        "Possibilidades de Desenvolvimento": [
            {
                "acao": "Mapear necessidades de capacitação por área",
                "responsavel": "RH",
                "prazo_dias": 30,
                "indicador": "Levantamento de necessidades concluído",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar Trilhas de Carreira Personalizadas (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 90,
                "indicador": "Trilhas de carreira definidas para todas as funções",
                "prioridade": "ALTA"
            },
            {
                "acao": "Ampliar orçamento de treinamentos",
                "responsavel": "Diretoria",
                "prazo_dias": 60,
                "indicador": "Orçamento aprovado com aumento de 30%",
                "prioridade": "MÉDIA"
            }
        ],
        "Significado do Trabalho": [
            {
                "acao": "Fortalecer comunicação sobre resultados e impacto do trabalho",
                "responsavel": "Liderança",
                "prazo_dias": 30,
                "indicador": "Reuniões mensais de resultados implementadas",
                "prioridade": "ALTA"
            },
            {
                "acao": "Criar rituais de celebração de conquistas",
                "responsavel": "RH/Liderança",
                "prazo_dias": 30,
                "indicador": "Calendário de celebrações definido",
                "prioridade": "MÉDIA"
            },
            {
                "acao": "Implementar Programa Retenção de Pessoas - Cultura Organizacional (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 90,
                "indicador": "Programa de cultura implementado",
                "prioridade": "ALTA"
            }
        ],
        "Reconhecimento": [
            {
                "acao": "Criar política formal de reconhecimento",
                "responsavel": "Diretoria",
                "prazo_dias": 60,
                "indicador": "Política de reconhecimento aprovada e divulgada",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar Avaliação de Desempenho & Meritocracia (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 90,
                "indicador": "Sistema de avaliação implementado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Vincular reconhecimento a resultados mensuráveis",
                "responsavel": "Gestão",
                "prazo_dias": 90,
                "indicador": "Critérios de reconhecimento definidos",
                "prioridade": "MÉDIA"
            }
        ],
        "Qualidade da Liderança": [
            {
                "acao": "Contratar Desenvolvimento da Liderança - Assessment e Coaching (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 30,
                "indicador": "Contrato assinado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Aplicar avaliação 360º em todos os líderes",
                "responsavel": "Consultoria Externa",
                "prazo_dias": 60,
                "indicador": "100% dos líderes avaliados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar mentoria entre líderes seniores e júniores",
                "responsavel": "RH/Liderança",
                "prazo_dias": 90,
                "indicador": "10 duplas de mentoria formadas",
                "prioridade": "MÉDIA"
            }
        ],
        "Suporte Social do Supervisor": [
            {
                "acao": "Treinar líderes em gestão de pessoas e comunicação",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "100% dos líderes treinados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar reuniões 1-on-1 regulares",
                "responsavel": "Liderança",
                "prazo_dias": 30,
                "indicador": "Calendário de 1-on-1 estabelecido",
                "prioridade": "ALTA"
            },
            {
                "acao": "Criar canal de feedback contínuo",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Ferramenta de feedback implementada",
                "prioridade": "MÉDIA"
            }
        ],
        "Suporte Social dos Colegas": [
            {
                "acao": "Promover atividades de integração entre equipes",
                "responsavel": "RH",
                "prazo_dias": 30,
                "indicador": "2 eventos de integração realizados",
                "prioridade": "MÉDIA"
            },
            {
                "acao": "Criar espaços de convivência e colaboração",
                "responsavel": "Facilities/RH",
                "prazo_dias": 90,
                "indicador": "Espaços de convivência implementados",
                "prioridade": "MÉDIA"
            },
            {
                "acao": "Implementar programa de team building",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Programa de team building contratado",
                "prioridade": "BAIXA"
            }
        ],
        "Comunidade Social no Trabalho": [
            {
                "acao": "Implementar Pesquisa de Clima & Engajamento (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Pesquisa aplicada e resultados analisados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Criar comitês de colaboradores por tema",
                "responsavel": "RH",
                "prazo_dias": 90,
                "indicador": "3 comitês formados e ativos",
                "prioridade": "MÉDIA"
            },
            {
                "acao": "Fortalecer valores e cultura organizacional",
                "responsavel": "Diretoria/RH",
                "prazo_dias": 90,
                "indicador": "Programa de cultura implementado",
                "prioridade": "MÉDIA"
            }
        ],
        "Insegurança no Trabalho": [
            {
                "acao": "Aumentar transparência sobre situação da empresa",
                "responsavel": "Diretoria",
                "prazo_dias": 30,
                "indicador": "Reuniões trimestrais de transparência implementadas",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar Trilhas de Carreira e Programa Retenção (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 90,
                "indicador": "Programa de retenção implementado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Criar plano de sucessão e desenvolvimento",
                "responsavel": "RH/Gestão",
                "prazo_dias": 90,
                "indicador": "Plano de sucessão documentado",
                "prioridade": "MÉDIA"
            }
        ],
        "Justiça e Respeito": [
            {
                "acao": "Aumentar transparência em processos de RH",
                "responsavel": "RH",
                "prazo_dias": 30,
                "indicador": "Processos de RH documentados e divulgados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar Programa de Cargos & Salários (Empório do Líder)",
                "responsavel": "RH/Diretoria",
                "prazo_dias": 90,
                "indicador": "Programa de C&S implementado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Padronizar critérios de avaliação e promoção",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Critérios documentados e aprovados",
                "prioridade": "MÉDIA"
            }
        ],
        "Conflito Trabalho-Família": [
            {
                "acao": "Monitorar horas extras e sobrecarga",
                "responsavel": "RH/Gestão",
                "prazo_dias": 30,
                "indicador": "Sistema de monitoramento implementado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Oferecer workshops sobre gestão de tempo e prioridades",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "2 workshops realizados",
                "prioridade": "MÉDIA"
            },
            {
                "acao": "Criar benefícios voltados à família",
                "responsavel": "RH/Diretoria",
                "prazo_dias": 90,
                "indicador": "Novos benefícios aprovados e implementados",
                "prioridade": "MÉDIA"
            }
        ],
        "Estresse": [
            {
                "acao": "Implementar técnicas de relaxamento e mindfulness",
                "responsavel": "SESMT/RH",
                "prazo_dias": 30,
                "indicador": "Programa de mindfulness implementado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Contratar Pesquisa de Clima com Foco em Saúde Mental (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Pesquisa aplicada e resultados analisados",
                "prioridade": "ALTA"
            },
            {
                "acao": "Monitorar indicadores de estresse (absenteísmo, turnover)",
                "responsavel": "RH",
                "prazo_dias": 30,
                "indicador": "Dashboard de indicadores implementado",
                "prioridade": "MÉDIA"
            }
        ],
        "Burnout": [
            {
                "acao": "Criar protocolo de identificação e prevenção de burnout",
                "responsavel": "SESMT/RH",
                "prazo_dias": 30,
                "indicador": "Protocolo documentado e divulgado",
                "prioridade": "ALTA"
            },
            {
                "acao": "Implementar Pesquisa de Clima com Foco em Saúde Mental (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Pesquisa aplicada com foco em burnout",
                "prioridade": "ALTA"
            },
            {
                "acao": "Oferecer apoio psicológico especializado",
                "responsavel": "SESMT/RH",
                "prazo_dias": 90,
                "indicador": "Serviço de apoio psicológico contratado",
                "prioridade": "ALTA"
            }
        ],
        "Sintomas Depressivos": [
            {
                "acao": "Disponibilizar canais de suporte emocional",
                "responsavel": "SESMT/RH",
                "prazo_dias": 30,
                "indicador": "Canais de suporte divulgados e ativos",
                "prioridade": "ALTA"
            },
            {
                "acao": "Contratar Pesquisa de Clima com Foco em Saúde Mental (Empório do Líder)",
                "responsavel": "RH",
                "prazo_dias": 60,
                "indicador": "Pesquisa aplicada com foco em saúde mental",
                "prioridade": "ALTA"
            },
            {
                "acao": "Criar ambiente acolhedor e de escuta",
                "responsavel": "Liderança/RH",
                "prazo_dias": 60,
                "indicador": "Treinamento de líderes em escuta ativa realizado",
                "prioridade": "MÉDIA"
            }
        ]
    }
    
    # Classificar dimensões por risco
    riscos_criticos = []
    riscos_moderados = []
    
    for dimensao, pontuacao in medias_dimensoes.items():
        # Determinar tipo de dimensão (exposição ou recurso)
        dimensoes_exposicao = ["Demandas Quantitativas", "Ritmo de Trabalho", "Demandas Emocionais", 
                              "Conflito Trabalho-Família", "Estresse", "Burnout", "Sintomas Depressivos"]
        
        if dimensao in dimensoes_exposicao:
            # Para exposição: quanto maior, pior
            if pontuacao >= 67:
                riscos_criticos.append((dimensao, pontuacao))
            elif pontuacao >= 33:
                riscos_moderados.append((dimensao, pontuacao))
        else:
            # Para recursos: quanto menor, pior
            if pontuacao <= 33:
                riscos_criticos.append((dimensao, pontuacao))
            elif pontuacao <= 67:
                riscos_moderados.append((dimensao, pontuacao))
    
    # Ordenar por gravidade
    riscos_criticos.sort(key=lambda x: x[1], reverse=True)
    riscos_moderados.sort(key=lambda x: x[1], reverse=True)
    
    # Gerar plano de ação
    plano_acao = []
    data_inicio = datetime.now()
    
    # Ações prioritárias (riscos críticos + top 5 moderados)
    dimensoes_prioritarias = [d[0] for d in riscos_criticos] + [d[0] for d in riscos_moderados[:5]]
    
    for dimensao in dimensoes_prioritarias:
        if dimensao in acoes_db:
            acoes = acoes_db[dimensao]
            pontuacao = medias_dimensoes[dimensao]
            
            # Adicionar as 2 primeiras ações de cada dimensão
            for acao_info in acoes[:2]:
                data_conclusao = data_inicio + timedelta(days=acao_info["prazo_dias"])
                
                plano_acao.append({
                    "prioridade": acao_info["prioridade"],
                    "dimensao": dimensao,
                    "pontuacao": pontuacao,
                    "acao": acao_info["acao"],
                    "responsavel": acao_info["responsavel"],
                    "data_inicio": data_inicio.strftime("%d/%m/%Y"),
                    "data_conclusao": data_conclusao.strftime("%d/%m/%Y"),
                    "prazo_dias": acao_info["prazo_dias"],
                    "indicador": acao_info["indicador"],
                    "status": "Não iniciado",
                    "trabalhadores_atingidos": num_trabalhadores
                })
    
    return plano_acao


def gerar_recomendacoes_personalizadas(classificacoes, medias):
    """
    Gera recomendações personalizadas baseadas nos resultados do COPSOQ III.
    
    Args:
        classificacoes: Dict com classificações de risco por dimensão
        medias: Dict com pontuações (0-100) por dimensão
    
    Returns:
        String com texto formatado das recomendações
    """
    
    # Dicionário de recomendações por dimensão
    recomendacoes_db = {
        "Demandas Quantitativas": {
            "critico": {
                "texto": "A sobrecarga de trabalho é significativa, com risco elevado de estresse e esgotamento profissional. Esta situação demanda ação imediata.",
                "acoes": [
                    "Realizar mapeamento detalhado da carga de trabalho por função (15 dias)",
                    "Redistribuir demandas entre equipes ou contratar reforços (30 dias)",
                    "Revisar prazos e metas para torná-los realistas (30 dias)",
                    "Implementar sistema de priorização de tarefas (60 dias)"
                ],
                "servico": "Consultoria em Gestão de Processos e Análise Ergonômica do Trabalho (AET)",
                "impacto": "Redução de 30-40% na percepção de sobrecarga em 3-6 meses"
            },
            "moderado": {
                "texto": "Há momentos de acúmulo de trabalho que podem gerar pressão. Atenção preventiva é recomendada.",
                "acoes": [
                    "Monitorar picos de demanda e identificar causas (30 dias)",
                    "Revisar distribuição de tarefas nas áreas críticas (60 dias)",
                    "Estabelecer pausas programadas durante o expediente (imediato)"
                ],
                "servico": "Programa de Qualidade de Vida e Gestão do Tempo",
                "impacto": "Melhoria de 15-20 pontos na dimensão em 3 meses"
            }
        },
        
        "Ritmo de Trabalho": {
            "critico": {
                "texto": "O ritmo de trabalho é excessivamente acelerado, com alto risco de burnout e problemas de saúde.",
                "acoes": [
                    "Revisar processos para eliminar atividades desnecessárias (30 dias)",
                    "Implementar pausas obrigatórias conforme NR-17 (imediato)",
                    "Adequar jornadas de trabalho e considerar flexibilização (60 dias)",
                    "Criar política de desconexão digital fora do expediente (30 dias)"
                ],
                "servico": "Consultoria em Ergonomia Organizacional e Programa de Bem-Estar",
                "impacto": "Redução de 25-35% no ritmo percebido em 3-6 meses"
            },
            "moderado": {
                "texto": "O ritmo de trabalho é acelerado em alguns momentos. Atenção para evitar fadiga crônica.",
                "acoes": [
                    "Identificar períodos de maior pressão temporal (30 dias)",
                    "Implementar ginástica laboral e pausas ativas (imediato)",
                    "Revisar prazos em projetos críticos (60 dias)"
                ],
                "servico": "Programa de Ginástica Laboral e Gestão de Energia",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Demandas Emocionais": {
            "critico": {
                "texto": "Alta exigência de envolvimento emocional no trabalho, com risco de exaustão emocional e compassion fatigue.",
                "acoes": [
                    "Implementar Programa de Apoio ao Colaborador (EAP) com suporte psicológico (imediato)",
                    "Realizar workshops sobre gestão emocional e autocuidado (30 dias)",
                    "Criar espaços de descompressão e apoio entre pares (30 dias)",
                    "Estabelecer rodízio em funções emocionalmente desgastantes (60 dias)"
                ],
                "servico": "Programa de Apoio ao Colaborador (EAP) e Workshops de Saúde Mental",
                "impacto": "Redução de 20-30% na exaustão emocional em 3-6 meses"
            },
            "moderado": {
                "texto": "Há exigência moderada de envolvimento emocional, que pode ser desgastante para alguns colaboradores.",
                "acoes": [
                    "Oferecer treinamento em inteligência emocional (60 dias)",
                    "Criar rituais de acolhimento e escuta (30 dias)",
                    "Disponibilizar canais de suporte emocional (30 dias)"
                ],
                "servico": "Treinamento em Inteligência Emocional e Comunicação Não-Violenta",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Influência no Trabalho": {
            "desfavoravel": {
                "texto": "Os colaboradores sentem que têm pouca ou nenhuma autonomia sobre seu trabalho, o que gera desmotivação e baixo engajamento.",
                "acoes": [
                    "Revisar modelo de gestão para aumentar autonomia (60 dias)",
                    "Implementar metodologias ágeis com times auto-organizados (90 dias)",
                    "Criar comitês participativos para decisões que afetam o trabalho (30 dias)",
                    "Treinar lideranças em delegação e empowerment (60 dias)"
                ],
                "servico": "Consultoria em Redesenho Organizacional e Desenvolvimento de Lideranças",
                "impacto": "Aumento de 25-35 pontos na autonomia percebida em 6 meses"
            },
            "intermediario": {
                "texto": "A autonomia é parcial. Existem oportunidades para aumentar a participação dos colaboradores nas decisões.",
                "acoes": [
                    "Ampliar poder de decisão em tarefas do dia a dia (30 dias)",
                    "Criar canais de sugestões e inovação (60 dias)",
                    "Envolver equipes em planejamento de projetos (60 dias)"
                ],
                "servico": "Programa de Gestão Participativa e Inovação",
                "impacto": "Melhoria de 15-20 pontos na dimensão em 3 meses"
            }
        },
        
        "Possibilidades de Desenvolvimento": {
            "desfavoravel": {
                "texto": "Faltam oportunidades de aprendizado e desenvolvimento de novas habilidades, gerando estagnação profissional e risco de perda de talentos.",
                "acoes": [
                    "Criar Plano de Desenvolvimento Individual (PDI) para todos os colaboradores (60 dias)",
                    "Implementar programa de educação continuada (90 dias)",
                    "Estabelecer trilhas de carreira claras (90 dias)",
                    "Criar programa de mentoria interna (60 dias)"
                ],
                "servico": "Programa de Desenvolvimento de Carreira e Educação Corporativa",
                "impacto": "Aumento de 30-40 pontos na percepção de desenvolvimento em 6 meses"
            },
            "intermediario": {
                "texto": "As oportunidades de desenvolvimento são pontuais. É possível ampliar programas de capacitação.",
                "acoes": [
                    "Mapear necessidades de capacitação por área (30 dias)",
                    "Ampliar orçamento de treinamentos (60 dias)",
                    "Criar biblioteca de cursos online (30 dias)"
                ],
                "servico": "Consultoria em Educação Corporativa",
                "impacto": "Melhoria de 15-20 pontos na dimensão em 3 meses"
            }
        },
        
        "Significado do Trabalho": {
            "desfavoravel": {
                "texto": "Os colaboradores não veem propósito ou significado em seu trabalho, o que afeta profundamente o engajamento e a motivação.",
                "acoes": [
                    "Realizar workshops sobre propósito organizacional e individual (30 dias)",
                    "Comunicar impacto do trabalho de cada área nos resultados da empresa (imediato)",
                    "Conectar atividades diárias aos valores e missão da organização (60 dias)",
                    "Criar programa de reconhecimento de contribuições significativas (60 dias)"
                ],
                "servico": "Consultoria em Cultura Organizacional e Programa de Engajamento",
                "impacto": "Aumento de 25-35 pontos no senso de propósito em 6 meses"
            },
            "intermediario": {
                "texto": "O senso de propósito é moderado. Ações de comunicação sobre o impacto do trabalho podem ajudar.",
                "acoes": [
                    "Fortalecer comunicação sobre resultados e impacto (30 dias)",
                    "Criar rituais de celebração de conquistas (imediato)",
                    "Envolver equipes em projetos estratégicos (60 dias)"
                ],
                "servico": "Programa de Comunicação Interna e Engajamento",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Reconhecimento": {
            "desfavoravel": {
                "texto": "Falta de valorização e reconhecimento no trabalho, o que gera desmotivação, baixa moral e alta rotatividade.",
                "acoes": [
                    "Implementar política formal de reconhecimento (30 dias)",
                    "Criar programa de meritocracia com critérios claros (60 dias)",
                    "Treinar lideranças em feedback positivo e valorização (30 dias)",
                    "Estabelecer rituais de reconhecimento público (imediato)"
                ],
                "servico": "Consultoria em Gestão de Pessoas e Programa de Reconhecimento",
                "impacto": "Aumento de 30-40 pontos na percepção de reconhecimento em 6 meses"
            },
            "intermediario": {
                "texto": "O reconhecimento é pontual, mas sem consistência. É necessário fortalecer a cultura de valorização.",
                "acoes": [
                    "Padronizar práticas de reconhecimento (30 dias)",
                    "Criar canal de elogios entre pares (30 dias)",
                    "Vincular reconhecimento a resultados (60 dias)"
                ],
                "servico": "Programa de Cultura de Reconhecimento",
                "impacto": "Melhoria de 15-20 pontos na dimensão em 3 meses"
            }
        },
        
        "Qualidade da Liderança": {
            "desfavoravel": {
                "texto": "A liderança é percebida como pouco eficaz, com falhas no planejamento, comunicação e suporte. Esta é uma dimensão crítica que afeta todas as outras.",
                "acoes": [
                    "Realizar Assessment 360° de competências de liderança (30 dias)",
                    "Implementar Programa de Desenvolvimento de Lideranças intensivo (60 dias)",
                    "Oferecer coaching executivo para líderes com maior gap (90 dias)",
                    "Criar rituais de feedback entre líderes e liderados (imediato)",
                    "Estabelecer indicadores de qualidade da liderança (30 dias)"
                ],
                "servico": "Programa de Desenvolvimento de Lideranças e Coaching Executivo",
                "impacto": "Melhoria de 30-40 pontos na qualidade da liderança em 6-12 meses"
            },
            "intermediario": {
                "texto": "A liderança apresenta pontos fortes e fracos. Recomenda-se treinamento em gestão de pessoas.",
                "acoes": [
                    "Oferecer treinamento em habilidades de liderança (60 dias)",
                    "Criar comunidade de prática entre líderes (30 dias)",
                    "Implementar mentoria de líderes seniores para júniores (60 dias)"
                ],
                "servico": "Treinamento em Liderança e Mentoria",
                "impacto": "Melhoria de 15-20 pontos na dimensão em 3-6 meses"
            }
        },
        
        "Suporte Social do Supervisor": {
            "desfavoravel": {
                "texto": "Os colaboradores não percebem apoio adequado de suas lideranças diretas, afetando o clima e o engajamento.",
                "acoes": [
                    "Treinar líderes em escuta ativa e empatia (30 dias)",
                    "Estabelecer reuniões 1-on-1 semanais obrigatórias (imediato)",
                    "Criar protocolo de suporte em situações de dificuldade (30 dias)",
                    "Avaliar líderes por qualidade do suporte oferecido (60 dias)"
                ],
                "servico": "Programa de Desenvolvimento de Lideranças com foco em Suporte",
                "impacto": "Aumento de 25-35 pontos na percepção de suporte em 6 meses"
            },
            "intermediario": {
                "texto": "O suporte da liderança é parcial, porém ainda aquém do ideal para um ambiente de confiança.",
                "acoes": [
                    "Fortalecer comunicação entre líderes e equipes (30 dias)",
                    "Criar canais de feedback sobre suporte (30 dias)",
                    "Oferecer treinamento em gestão de pessoas (60 dias)"
                ],
                "servico": "Treinamento em Gestão de Pessoas e Comunicação",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Suporte Social dos Colegas": {
            "desfavoravel": {
                "texto": "O ambiente entre colegas é marcado por falta de cooperação e suporte, o que pode gerar isolamento e conflitos.",
                "acoes": [
                    "Realizar dinâmicas de team building e integração (30 dias)",
                    "Implementar programas de trabalho colaborativo (60 dias)",
                    "Criar espaços de convivência e interação (30 dias)",
                    "Treinar equipes em comunicação e resolução de conflitos (60 dias)"
                ],
                "servico": "Programa de Fortalecimento de Equipes e Team Building",
                "impacto": "Aumento de 20-30 pontos na colaboração em 6 meses"
            },
            "intermediario": {
                "texto": "A colaboração entre colegas existe, mas pode ser aprimorada para fortalecer o espírito de equipe.",
                "acoes": [
                    "Promover atividades de integração regulares (30 dias)",
                    "Criar projetos colaborativos entre áreas (60 dias)",
                    "Reconhecer comportamentos de ajuda mútua (imediato)"
                ],
                "servico": "Programa de Integração e Colaboração",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Justiça e Respeito": {
            "desfavoravel": {
                "texto": "Há percepção de injustiça ou desrespeito no tratamento dos colaboradores, gerando um clima de desconfiança e insatisfação.",
                "acoes": [
                    "Revisar políticas de RH para garantir equidade (60 dias)",
                    "Implementar canal de denúncias e ouvidoria (30 dias)",
                    "Treinar lideranças em gestão ética e justa (60 dias)",
                    "Realizar auditoria de práticas de gestão de pessoas (90 dias)",
                    "Comunicar critérios de decisões que afetam colaboradores (imediato)"
                ],
                "servico": "Consultoria em Compliance de RH e Programa de Ética Organizacional",
                "impacto": "Aumento de 25-35 pontos na percepção de justiça em 6-12 meses"
            },
            "intermediario": {
                "texto": "As práticas de gestão são percebidas como justas na maior parte do tempo, mas há espaço para melhorias.",
                "acoes": [
                    "Aumentar transparência em processos de RH (30 dias)",
                    "Criar comitê de ética e conduta (60 dias)",
                    "Padronizar critérios de avaliação e promoção (60 dias)"
                ],
                "servico": "Consultoria em Governança de RH",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Comunidade Social no Trabalho": {
            "desfavoravel": {
                "texto": "O ambiente de trabalho apresenta sinais de conflito, desconfiança ou isolamento social, prejudicando o clima organizacional.",
                "acoes": [
                    "Realizar diagnóstico de clima organizacional aprofundado (30 dias)",
                    "Implementar programa de cultura e valores (90 dias)",
                    "Criar grupos de afinidade e comunidades de prática (60 dias)",
                    "Promover eventos de integração e confraternização (imediato)",
                    "Treinar equipes em comunicação não-violenta (60 dias)"
                ],
                "servico": "Consultoria em Cultura Organizacional e Programa de Clima",
                "impacto": "Melhoria de 25-35 pontos no clima social em 6-12 meses"
            },
            "intermediario": {
                "texto": "O clima social tem pontos positivos e negativos, requerendo ajustes em cultura e comunicação.",
                "acoes": [
                    "Fortalecer comunicação interna (30 dias)",
                    "Criar rituais de convivência (30 dias)",
                    "Promover ações de voluntariado corporativo (60 dias)"
                ],
                "servico": "Programa de Comunicação Interna e Engajamento",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Conflito Trabalho-Família": {
            "critico": {
                "texto": "A interferência do trabalho na vida pessoal é alta, com risco de estresse, problemas familiares e burnout.",
                "acoes": [
                    "Implementar política de flexibilidade de horários (30 dias)",
                    "Oferecer home office ou modelo híbrido (30 dias)",
                    "Revisar jornadas e horas extras (imediato)",
                    "Criar programa de apoio à família (60 dias)",
                    "Estabelecer política de desconexão digital (30 dias)"
                ],
                "servico": "Consultoria em Qualidade de Vida e Programa de Equilíbrio Trabalho-Vida",
                "impacto": "Redução de 25-35% no conflito trabalho-família em 6 meses"
            },
            "moderado": {
                "texto": "O trabalho ocasionalmente interfere na vida pessoal, gerando necessidade de atenção ao equilíbrio.",
                "acoes": [
                    "Monitorar horas extras e sobrecarga (30 dias)",
                    "Oferecer workshops sobre gestão de tempo e prioridades (60 dias)",
                    "Criar benefícios voltados à família (60 dias)"
                ],
                "servico": "Programa de Qualidade de Vida",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Insegurança no Trabalho": {
            "critico": {
                "texto": "A insegurança em relação ao futuro no trabalho é alta, sendo um fator de estresse significativo e afetando o desempenho.",
                "acoes": [
                    "Comunicar de forma transparente sobre situação da empresa (imediato)",
                    "Estabelecer planos de carreira claros (60 dias)",
                    "Criar programas de retenção de talentos (90 dias)",
                    "Oferecer capacitação para aumentar empregabilidade (60 dias)"
                ],
                "servico": "Consultoria em Comunicação Organizacional e Gestão de Mudanças",
                "impacto": "Redução de 20-30% na insegurança em 6 meses"
            },
            "moderado": {
                "texto": "Existe alguma preocupação com a segurança no emprego, o que pode gerar ansiedade.",
                "acoes": [
                    "Melhorar comunicação sobre perspectivas futuras (30 dias)",
                    "Criar programas de desenvolvimento (60 dias)",
                    "Reconhecer e valorizar contribuições (imediato)"
                ],
                "servico": "Programa de Comunicação e Engajamento",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Estresse": {
            "critico": {
                "texto": "Níveis de estresse elevados indicam necessidade urgente de intervenções para promover o bem-estar e prevenir problemas de saúde.",
                "acoes": [
                    "Implementar Programa de Apoio ao Colaborador (EAP) imediatamente",
                    "Oferecer workshops sobre gestão de estresse (30 dias)",
                    "Criar espaços de descompressão no ambiente de trabalho (30 dias)",
                    "Revisar causas organizacionais do estresse (dimensões de exposição)",
                    "Disponibilizar suporte psicológico (imediato)"
                ],
                "servico": "Programa de Apoio ao Colaborador (EAP) e Workshops de Saúde Mental",
                "impacto": "Redução de 20-30% nos níveis de estresse em 3-6 meses"
            },
            "moderado": {
                "texto": "Há sinais de estresse que merecem atenção para evitar o agravamento.",
                "acoes": [
                    "Oferecer técnicas de relaxamento e mindfulness (30 dias)",
                    "Criar programa de atividade física (60 dias)",
                    "Monitorar indicadores de estresse (30 dias)"
                ],
                "servico": "Programa de Qualidade de Vida e Bem-Estar",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3 meses"
            }
        },
        
        "Burnout": {
            "critico": {
                "texto": "Sinais claros de burnout, como exaustão e distanciamento emocional. Ações urgentes são necessárias para evitar afastamentos e problemas graves de saúde.",
                "acoes": [
                    "Identificar colaboradores em risco e oferecer suporte imediato",
                    "Implementar Programa de Apoio ao Colaborador (EAP) com urgência",
                    "Revisar cargas de trabalho e redistribuir demandas (imediato)",
                    "Oferecer licenças remuneradas para recuperação quando necessário",
                    "Atacar causas organizacionais (demandas, liderança, reconhecimento)"
                ],
                "servico": "Programa de Apoio ao Colaborador (EAP) e Consultoria em Prevenção de Burnout",
                "impacto": "Redução de 25-35% nos sinais de burnout em 6-12 meses"
            },
            "moderado": {
                "texto": "Sinais de esgotamento estão presentes e devem ser monitorados para prevenir o burnout.",
                "acoes": [
                    "Criar programa de prevenção de burnout (60 dias)",
                    "Oferecer pausas e férias adequadas (imediato)",
                    "Monitorar sinais de exaustão (30 dias)"
                ],
                "servico": "Programa de Prevenção de Burnout e Qualidade de Vida",
                "impacto": "Melhoria de 15-20 pontos na dimensão em 3-6 meses"
            }
        },
        
        "Sintomas Depressivos": {
            "critico": {
                "texto": "Sintomas depressivos significativos são relatados, sendo crucial oferecer suporte psicológico e organizacional urgente.",
                "acoes": [
                    "Implementar Programa de Apoio ao Colaborador (EAP) com psicólogos (imediato)",
                    "Criar campanha de conscientização sobre saúde mental (30 dias)",
                    "Treinar lideranças para identificar sinais de alerta (30 dias)",
                    "Revisar fatores organizacionais que afetam bem-estar emocional",
                    "Estabelecer parceria com clínicas de saúde mental (30 dias)"
                ],
                "servico": "Programa de Apoio ao Colaborador (EAP) e Campanha de Saúde Mental",
                "impacto": "Redução de 20-30% nos sintomas depressivos em 6-12 meses"
            },
            "moderado": {
                "texto": "Presença de sintomas depressivos leves a moderados, indicando necessidade de apoio.",
                "acoes": [
                    "Disponibilizar canais de suporte emocional (30 dias)",
                    "Oferecer workshops sobre saúde mental (60 dias)",
                    "Criar ambiente acolhedor e de escuta (imediato)"
                ],
                "servico": "Programa de Saúde Mental e Bem-Estar",
                "impacto": "Melhoria de 10-15 pontos na dimensão em 3-6 meses"
            }
        }
    }
    
    # Separa dimensões por nível de risco
    riscos_criticos = []
    riscos_moderados = []
    
    for dimensao, classif in classificacoes.items():
        risco = classif.get("risco", "")
        pontuacao = medias.get(dimensao, 0)
        
        # Verifica se a dimensão tem recomendações definidas
        if dimensao not in recomendacoes_db:
            continue
        
        # Classifica por nível de risco
        if risco in ["Risco Elevado", "Desfavorável"]:
            # Determina a chave correta (critico ou desfavoravel)
            chave = "critico" if "Risco" in risco else "desfavoravel"
            if chave in recomendacoes_db[dimensao]:
                riscos_criticos.append((dimensao, pontuacao, recomendacoes_db[dimensao][chave]))
        elif risco in ["Risco Moderado", "Intermediário"]:
            # Determina a chave correta (moderado ou intermediario)
            chave = "moderado" if "Risco" in risco else "intermediario"
            if chave in recomendacoes_db[dimensao]:
                riscos_moderados.append((dimensao, pontuacao, recomendacoes_db[dimensao][chave]))
    
    # Ordena por pontuação (mais crítico primeiro)
    # Para exposição/resultado: maior pontuação = pior
    # Para recursos: menor pontuação = pior
    riscos_criticos.sort(key=lambda x: x[1], reverse=False)  # Menor pontuação primeiro para recursos
    riscos_moderados.sort(key=lambda x: x[1], reverse=False)
    
    # Monta o texto das recomendações
    texto = "Com base nos resultados obtidos, apresentamos recomendações priorizadas por nível de risco e urgência de intervenção.\n\n"
    
    # Riscos Críticos
    if riscos_criticos:
        texto += "[CAIXA]DIMENSÕES EM RISCO CRÍTICO[/CAIXA]\n"
        texto += "As dimensões abaixo apresentam situação crítica e demandam ação imediata:\n\n"
        
        for dimensao, pontuacao, rec in riscos_criticos:
            texto += f"[NEGRITO]{dimensao} (Pontuação: {pontuacao:.1f}/100)[/NEGRITO]\n"
            texto += f"{rec['texto']}\n\n"
            texto += "Ações Recomendadas:\n"
            for i, acao in enumerate(rec['acoes'], 1):
                texto += f"{i}. {acao}\n"
            texto += f"\nServiço Aplicável: {rec['servico']}\n"
            texto += f"Impacto Esperado: {rec['impacto']}\n\n"
    
    # Riscos Moderados
    if riscos_moderados:
        texto += "[CAIXA]DIMENSÕES EM RISCO MODERADO[/CAIXA]\n"
        texto += "As dimensões abaixo requerem atenção preventiva:\n\n"
        
        for dimensao, pontuacao, rec in riscos_moderados:
            texto += f"[NEGRITO]{dimensao} (Pontuação: {pontuacao:.1f}/100)[/NEGRITO]\n"
            texto += f"{rec['texto']}\n\n"
            texto += "Ações Recomendadas:\n"
            for i, acao in enumerate(rec['acoes'], 1):
                texto += f"{i}. {acao}\n"
            texto += f"\nServiço Aplicável: {rec['servico']}\n"
            texto += f"Impacto Esperado: {rec['impacto']}\n\n"
    
    # Recomendações Gerais
    texto += "[CAIXA]RECOMENDAÇÕES GERAIS DE MONITORAMENTO[/CAIXA]\n"
    texto += "Independente dos riscos identificados, recomenda-se:\n\n"
    texto += "1. Reaplicar este Mapeamento de Riscos Psicossociais semestralmente para monitorar evolução\n"
    texto += "2. Integrar todas as ações ao Programa de Gerenciamento de Riscos (PGR) da empresa\n"
    texto += "3. Estabelecer indicadores de acompanhamento (absenteísmo, turnover, clima)\n"
    texto += "4. Criar comitê de saúde mental e bem-estar para coordenar ações\n"
    texto += "5. Comunicar de forma transparente as ações que serão implementadas\n\n"
    texto += "Em conformidade com a NR-1, todas as medidas preventivas e corretivas devem ser monitoradas de forma sistemática e documentadas no PGR.\n\n"
    
    # Próximos Passos
    texto += "[CAIXA]PRÓXIMOS PASSOS[/CAIXA]\n"
    texto += "Para garantir a efetividade das ações recomendadas, sugerimos:\n\n"
    texto += "1. Reunião de apresentação detalhada dos resultados com a liderança\n"
    texto += "2. Discussão e priorização conjunta das ações considerando contexto e recursos\n"
    texto += "3. Elaboração de cronograma de implementação realista\n"
    texto += "4. Definição de responsáveis e orçamento para cada ação\n"
    texto += "5. Estabelecimento de métricas de sucesso e acompanhamento\n\n"
    texto += "O Empório do Líder está à disposição para apoiar a implementação de todas as ações recomendadas, "
    texto += "oferecendo soluções customizadas que atendam às necessidades específicas da sua organização."
    
    return texto

# ------------------------------
# Funções auxiliares
# ------------------------------


def converter_respostas(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Escala COPSOQ III (0-4)
    # Mapeamento em minúsculas para compatibilidade
    mapa_copsoq = {
        "nunca/quase nunca": 0, "nunca": 0,
        "raramente": 1, "algumas vezes": 1,
        "às vezes": 2,
        "frequentemente": 3,
        "sempre": 4, "sempre ou quase sempre": 4
    }
    
    df = df_raw.copy()
    
    # Mapeia todas as colunas de respostas (assumindo que estão de 6 a 41)
    blocos_copsoq = list(range(6, 42))
    for i in blocos_copsoq:
        # Assegura que a coluna é do tipo string antes de usar .str
        if df.iloc[:, i].dtype == 'object':
            df.iloc[:, i] = df.iloc[:, i].str.strip().str.lower()
        df.iloc[:, i] = df.iloc[:, i].map(mapa_copsoq)

    # Trata itens com pontuação invertida (se houver)
    # Exemplo: df.iloc[:, COL_INVERTIDA] = 4 - df.iloc[:, COL_INVERTIDA]

    dados = pd.DataFrame()
    dados["Empresa"] = df.iloc[:, 1].fillna("Empresa_Desconhecida")
    dados["Data"] = pd.Timestamp.today().strftime("%d/%m/%Y")
    dados["Unidade"] = df.iloc[:, 2].fillna("Não Informada")

    # Novas dimensões COPSOQ III e seus respectivos índices de coluna
    dimensoes = {
        "Demandas Quantitativas": list(range(6, 8)),
        "Ritmo de Trabalho": list(range(8, 10)),
        "Demandas Emocionais": list(range(10, 12)),
        "Influência no Trabalho": list(range(12, 14)),
        "Possibilidades de Desenvolvimento": list(range(14, 16)),
        "Significado do Trabalho": list(range(16, 18)),
        "Reconhecimento": list(range(18, 20)),
        "Qualidade da Liderança": list(range(20, 24)),
        "Suporte Social do Supervisor": list(range(24, 26)),
        "Suporte Social dos Colegas": list(range(26, 28)),
        "Justiça e Respeito": list(range(28, 30)),
        "Comunidade Social no Trabalho": list(range(30, 32)),
        "Conflito Trabalho-Família": list(range(32, 34)),
        "Insegurança no Trabalho": list(range(34, 36)),
        "Estresse": list(range(36, 38)),
        "Burnout": list(range(38, 40)),
        "Sintomas Depressivos": list(range(40, 42)),
    }

    for nome, idxs in dimensoes.items():
        # Calcula a média (escala 0-4) e converte para 0-100
        media_0_4 = df.iloc[:, idxs].mean(axis=1)
        dados[nome] = (media_0_4 * 100) / 4
    
    # Debug: mostra se há valores NaN
    print("\n=== DEBUG: Verificação de Dados ===")
    print(f"Total de colaboradores processados: {len(dados)}")
    for col in dados.columns:
        if col not in ['Empresa', 'Data', 'Unidade']:
            nan_count = dados[col].isna().sum()
            if nan_count > 0:
                print(f"ATENÇÃO: {col} tem {nan_count} valores NaN")
    print("="*40 + "\n")

    return dados


def gerar_grafico_radar(medias: dict, empresa: str) -> str:
    labels = list(medias.keys())
    valores = list(medias.values())
    
    # Debug: mostra os valores que serão plotados
    print("\n=== DEBUG: Valores do Gráfico Radar ===")
    for label, valor in zip(labels, valores):
        print(f"{label}: {valor:.2f}" if not (isinstance(valor, float) and np.isnan(valor)) else f"{label}: NaN")
    print("="*40 + "\n")
    
    # Tratamento de valores NaN - substitui por 0 se houver
    valores = [0 if (isinstance(v, float) and np.isnan(v)) else v for v in valores]
    
    valores += valores[:1]  # Fechar o radar
    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Adiciona linhas de grade para referência visual ANTES dos dados
    ax.plot(angles, [33] * (num_vars + 1), color='green', linestyle='--', linewidth=1.5, label='Limite Favorável (33)', zorder=1)
    ax.plot(angles, [67] * (num_vars + 1), color='red', linestyle='--', linewidth=1.5, label='Limite Desfavorável (67)', zorder=1)
    
    # Plota os dados da empresa POR CIMA das linhas de referência
    ax.plot(angles, valores, linewidth=3, color='blue', label='Empresa', zorder=3)
    ax.fill(angles, valores, color='blue', alpha=0.25, zorder=2)

    ax.set_yticklabels([]) # Remove os labels do eixo Y (0, 20, 40...)
    ax.set_ylim(0, 100) # Escala de 0 a 100

    # Ajusta os labels das dimensões para melhor legibilidade
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=8)
    
    # Adiciona legenda
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    
    fig.tight_layout()

    os.makedirs("laudos", exist_ok=True)
    nome_arquivo = os.path.join("laudos", f"{sanitize(empresa)}_grafico_radar_copsoq.png")
    plt.savefig(nome_arquivo, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return nome_arquivo


def classificar_dimensoes(medias: dict) -> dict:
    """Classifica dimensões COPSOQ III (escala 0-100)."""
    dimensoes_exposicao = [
        "Demandas Quantitativas", "Ritmo de Trabalho", "Demandas Emocionais",
        "Conflito Trabalho-Família", "Insegurança no Trabalho"
    ]
    dimensoes_recursos = [
        "Influência no Trabalho", "Possibilidades de Desenvolvimento", "Significado do Trabalho",
        "Reconhecimento", "Qualidade da Liderança", "Suporte Social do Supervisor",
        "Suporte Social dos Colegas", "Justiça e Respeito", "Comunidade Social no Trabalho"
    ]
    dimensoes_resultado = ["Estresse", "Burnout", "Sintomas Depressivos"]

    classificacoes = {}
    for dim, val in medias.items():
        risco = "N/A"
        if dim in dimensoes_exposicao or dim in dimensoes_resultado:
            if val >= 67: risco = "Risco Elevado"
            elif val >= 34: risco = "Risco Moderado"
            else: risco = "Risco Baixo"
        elif dim in dimensoes_recursos:
            if val >= 67: risco = "Favorável"
            elif val >= 34: risco = "Intermediário"
            else: risco = "Desfavorável"
        classificacoes[dim] = {"risco": risco}
    return classificacoes

def sanitize(name: str) -> str:
    name = re.sub(r"\s+", "_", str(name).strip())
    name = re.sub(r"[^\w\-\.]", "", name, flags=re.ASCII)
    return name or "Empresa"


# ------------------------------
# Geração do Laudo
# ------------------------------
def gerar_laudo_empresa(dados_empresa: pd.Series, num_trabalhadores=20):
    empresa = safe_text(dados_empresa.get('Empresa', "Empresa_Desconhecida"))
    data_str = dados_empresa.get('Data', "")
    try:
        data_obj = pd.to_datetime(data_str, dayfirst=True, errors='coerce')
        data_avaliacao = f"{data_obj.strftime('%B/%Y')}" if pd.notna(data_obj) else safe_text(data_str)
    except Exception:
        data_avaliacao = safe_text(data_str)
    unidade = safe_text(dados_empresa.get('Unidade', "Não Informada"))

    medias = {k: float(v) for k, v in dados_empresa.items() if k not in ['Empresa', 'Data', 'Unidade']}
    classificacoes = classificar_dimensoes(medias)
    grafico_path = gerar_grafico_radar(medias, empresa)

    pdf = LaudoNR1()
    pdf.add_page()

    pdf.add_title("Laudo Técnico - Mapeamento de Riscos Psicossociais (NR-1 e NR-17)")

    pdf.add_section_title("1. Identificação da Empresa")
    pdf.add_paragraph(f"Empresa: {empresa}\nData da Avaliação: {data_avaliacao}\nUnidade Avaliada: {unidade}")

    pdf.add_section_title("2. Objetivo do Laudo")
    pdf.add_paragraph(
        "Este laudo visa identificar e mensurar riscos psicossociais no ambiente de trabalho, em conformidade com a NR-1 "
        "(Gerenciamento de Riscos Ocupacionais – GRO) e a NR-17 (Ergonomia). A metodologia utilizada é o Copenhagen Psychosocial Questionnaire (COPSOQ III), "
        "um instrumento validado internacionalmente para esta finalidade."
    )

    pdf.add_section_title("3. Metodologia Utilizada")
    pdf.add_paragraph(
        "Foi aplicado o questionário COPSOQ III, de forma sigilosa e confidencial. Os resultados consolidados deste laudo "
        "deverão ser integrados ao PGR (Programa de Gerenciamento de Riscos) da empresa. "
        "Este laudo não possui caráter de diagnóstico clínico individual, mas sim de gestão organizacional preventiva e corretiva."
    )
    pdf.ln(3)
    pdf.add_table_metodologia()
    
    # Texto esclarecedor sobre integração ao GRO e limitação de escopo
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Integração ao Sistema de Gerenciamento de Riscos Ocupacionais (GRO) e Limitação de Escopo", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.ln(2)
    
    pdf.add_paragraph(
        "O presente Laudo de Avaliação dos Riscos Psicossociais foi elaborado em conformidade com as disposições da "
        "Norma Regulamentadora nº 1 (NR-1), que estabelece as diretrizes do Gerenciamento de Riscos Ocupacionais (GRO), "
        "e da Norma Regulamentadora nº 17 (NR-17), que trata da ergonomia e dos fatores psicossociais no trabalho."
    )
    pdf.ln(2)
    
    pdf.add_paragraph(
        "A metodologia utilizada baseia-se no modelo COPSOQ III – Copenhagen Psychosocial Questionnaire, instrumento "
        "cientificamente validado para identificação, mensuração e classificação dos fatores psicossociais e organizacionais "
        "que impactam a saúde mental e o bem-estar dos trabalhadores."
    )
    pdf.ln(2)
    
    pdf.add_paragraph(
        "Este laudo integra o sistema de gestão de riscos da empresa, representando o mapeamento e a avaliação dos riscos "
        "psicossociais, conforme previsto na NR-1, item 1.5.4.2."
    )
    pdf.ln(2)
    
    pdf.add_paragraph(
        "Ressalta-se que a Análise de Exposição Preliminar (AEP) dos riscos físicos, químicos, biológicos e ergonômicos "
        "deve ser conduzida por profissional legalmente habilitado na área de Segurança e Saúde no Trabalho, de modo a "
        "complementar o gerenciamento global dos riscos ocupacionais e garantir a conformidade integral com o Programa de "
        "Gerenciamento de Riscos (PGR) da organização."
    )
    pdf.ln(2)
    
    pdf.add_paragraph(
        "Assim, este documento compõe o conjunto técnico do GRO, atendendo às exigências legais referentes aos riscos "
        "psicossociais e servindo de subsídio para o planejamento das medidas preventivas, corretivas e de promoção de "
        "saúde mental no ambiente de trabalho."
    )

    pdf.add_page()
    pdf.add_section_title("4. Resultados Consolidados da Empresa")
    pdf.add_table_resultados(medias, classificacoes)
    pdf.ln(2)

    pdf.add_page()
    pdf.add_section_title("4.1 Tabela de Referência de Classificação (Escala 0-100)")
    pdf.add_table_referencias()

    pdf.add_page()
    pdf.add_section_title("4.2 Gráfico Radar - Dimensões Avaliadas")
    if os.path.exists(grafico_path):
        pdf.image(grafico_path, x=45, w=120)
    pdf.ln(2)
    
    pdf.add_page()
    pdf.add_section_title("5. Análise Interpretativa dos Resultados")
    pdf.add_interpretacao(classificacoes)

    # Gera Plano de Ação (antiga Seção 7 - Recomendações)
    pdf.add_page()
    pdf.add_section_title("6. Plano de Ação")
    
    # Texto introdutório conforme NR-1
    pdf.add_paragraph(
        "Em conformidade com a NR-1, subitem 1.5.5.2.2, este Plano de Ação apresenta as medidas preventivas e corretivas "
        "relacionadas aos riscos psicossociais identificados. Cada ação definida contém responsável, prazo de execução e "
        "indicadores de acompanhamento, compondo assim o Inventário de Riscos e o Plano de Ação do PGR (Programa de "
        "Gerenciamento de Riscos).\n\n"
        "As recomendações aqui estabelecidas representam os compromissos de gestão assumidos pela empresa, devendo ser "
        "implementados e monitorados periodicamente. Sua execução e atualização contínua são fundamentais para assegurar "
        "a conformidade legal, reduzir riscos ocupacionais e promover um ambiente de trabalho saudável e produtivo."
    )
    pdf.ln(5)
    
    # Gera recomendações personalizadas baseadas nos resultados
    recomendacoes_texto = gerar_recomendacoes_personalizadas(classificacoes, medias)
    pdf.add_recomendacoes(recomendacoes_texto)

    pdf.add_page()
    pdf.add_section_title("7. Considerações Finais")
    pdf.add_paragraph(
        "Este laudo atende às exigências da NR-1 no contexto do Gerenciamento de Riscos Psicossociais no trabalho, observando também a "
        "conexão com a NR-17. Os resultados devem ser incorporados ao Inventário do PGR, garantindo rastreabilidade. "
        "Ressalta-se que não possui caráter clínico individual, mas sim de gestão organizacional preventiva e corretiva."
    )
    pdf.add_section_title("SOMENTE PESSOAS FELIZES DÃO RESULTADOS EXTRAORDINÁRIOS")
    pdf.add_assinatura()

    os.makedirs("laudos", exist_ok=True)
    output_path = os.path.join("laudos", f"Laudo_COPSOQ_{sanitize(empresa)}.pdf")
    pdf.output(output_path)


# ------------------------------
# Fluxo principal
# ------------------------------
def main():
    entrada = "NR-1_COPSOQ_2025.xlsx"
    if not os.path.exists(entrada):
        print(f"Arquivo de entrada '{entrada}' não encontrado.")
        print("Por favor, crie um arquivo Excel com este nome, contendo os dados brutos do questionário COPSOQ III.")
        print("As respostas devem começar na coluna G (índice 6) e seguir a ordem das dimensões definidas no script.")
        # Criar um arquivo de exemplo para o usuário
        colunas_exemplo = ['Carimbo de data/hora', 'Empresa', 'Unidade', 'Setor', 'Cargo', 'Email'] \
                        + [f'Q{i+1}' for i in range(36)] # 36 perguntas de exemplo
        df_exemplo = pd.DataFrame(columns=colunas_exemplo)
        df_exemplo.to_excel(entrada, index=False)
        print(f"Um arquivo de exemplo '{entrada}' foi criado.")
        return

    df_raw = pd.read_excel(entrada)
    dados_final = converter_respostas(df_raw)

    # Salva os dados processados para verificação
    dados_final.to_excel("respostas_consolidadas_copsoq.xlsx", sheet_name="Respostas_0_100", index=False)

    # Gera um laudo consolidado para a média da empresa
    dados_consolidados_empresa = dados_final.drop(columns=['Empresa', 'Data', 'Unidade']).mean().to_frame().T
    dados_consolidados_empresa['Empresa'] = dados_final['Empresa'].iloc[0] if not dados_final.empty else 'Empresa Exemplo'
    dados_consolidados_empresa['Data'] = pd.Timestamp.today().strftime("%d/%m/%Y")
    dados_consolidados_empresa['Unidade'] = 'Consolidado'
    
    # Passa o número real de trabalhadores para o plano de ação
    num_trabalhadores = len(dados_final)
    gerar_laudo_empresa(dados_consolidados_empresa.iloc[0], num_trabalhadores)

    print("Processamento completo: respostas consolidadas e laudo geral gerados.")


if __name__ == "__main__":
    main()
