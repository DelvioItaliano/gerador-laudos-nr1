
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from fpdf import FPDF

interpretacoes = {
        "GAD-7": {
            "Baixo": "Os colaboradores apresentam baixa manifestação de sintomas ansiosos. A rotina de trabalho parece equilibrada do ponto de vista emocional.",
            "Moderado": "Há indícios de tensão emocional entre os colaboradores. Recomendam-se ações preventivas para evitar agravamento.",
            "Alto": "Os níveis de ansiedade são significativos e podem comprometer a saúde mental e produtividade. Intervenções urgentes são recomendadas."
        },
        "PHQ-9": {
            "Baixo": "Os sinais de depressão são mínimos ou inexistentes. O ambiente de trabalho tende a ser emocionalmente saudável.",
            "Moderado": "Indícios moderados de tristeza, desmotivação ou fadiga emocional. Pode haver impacto na performance.",
            "Alto": "Sinais importantes de sofrimento emocional. É essencial atuar com escuta, apoio psicológico e revisão de práticas organizacionais."
        },
        "SRQ-20": {
            "Baixo": "Os colaboradores demonstram boa adaptação emocional e pouca vulnerabilidade ao sofrimento psíquico.",
            "Moderado": "Há indícios de dificuldades emocionais que devem ser acompanhadas com atenção.",
            "Alto": "O risco psicossocial é elevado. É essencial mobilizar ações estruturadas para acolhimento e suporte."
        },
        "Apoio da Liderança": {
            "Baixo": "Os colaboradores não percebem apoio adequado de suas lideranças. Isso pode afetar o clima e o engajamento.",
            "Moderado": "Há um apoio parcial, porém ainda aquém do ideal.",
            "Alto": "As lideranças são percebidas como acolhedoras e presentes. Fator protetivo importante."
        },
        "Clima Organizacional": {
            "Baixo": "O ambiente de trabalho apresenta sinais de conflito, desconfiança ou desmotivação.",
            "Moderado": "O clima tem pontos positivos e negativos. Requer ajustes em cultura e comunicação.",
            "Alto": "Ambiente saudável, colaborativo e estimulante. Fortalece o bem-estar e o desempenho."
        },
        "Reconhecimento": {
            "Baixo": "Falta de valorização e reconhecimento no trabalho. Pode gerar desmotivação ou rotatividade.",
            "Moderado": "Reconhecimento pontual, mas sem consistência. É necessário fortalecer a cultura de valorização.",
            "Alto": "Os colaboradores se sentem valorizados. Isso gera engajamento e senso de pertencimento."
        },
        "Sobrecarga de Trabalho": {
            "Baixo": "Carga de trabalho equilibrada e bem distribuída.",
            "Moderado": "Demandas acima do confortável. Pode causar estresse ou queda de desempenho.",
            "Alto": "Sinais claros de sobrecarga. Alto risco de burnout e adoecimento mental. Medidas urgentes são recomendadas."
        }
    }


class LaudoNR1(FPDF):

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')


    def header(self):

        if os.path.exists("logo.png"):
                self.image("logo.png", x=10, y=8, w=25)

        # Define a fonte para o título
        self.set_font("Arial", "B", 14)
        self.set_xy(0, 15)  # Posição do título no centro verticalmente
        self.cell(0, 15, "Sua Consultoria de Gestão Estratégica de Pessoas", align="C")

        # Linha horizontal (subida para Y=30)
        self.set_xy(10, 40)
        self.set_draw_color(50, 50, 50)
        self.line(10, 35, 200, 35)
        self.set_y(40)  # Ajusta a próxima linha do texto abaixo da linha

    def footer(self):
            self.set_y(-25)
            self.set_draw_color(50, 50, 50)
            self.line(10, self.get_y(), 200, self.get_y())
            self.set_y(-20)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, "Emporio do Lider - Gestao de Pessoas e Treinamento", ln=1, align="C")
            self.cell(0, 5, "CNPJ: 31.505.935/0001-53", ln=1, align="C")
            self.cell(0, 5, "Telefone: (11) 97238-5938 | Site: www.emporiodolider.com.br", align="C")

    def add_interpretacao_automatica(self, classificacoes):
        self.ln(10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "5. Análise Interpretativa dos Resultados", ln=True)
        self.set_font("Arial", "", 10)

        for dimensao, risco in classificacoes.items():
            self.set_font("Arial", "B", 10)
            self.cell(0, 8, f"{dimensao} - Risco {risco}", ln=True)
            self.set_font("Arial", "", 10)
            texto = interpretacoes.get(dimensao, {}).get(risco, "Sem interpretação disponível.")
            self.multi_cell(0, 8, texto.encode('latin-1', 'replace').decode('latin-1'))
            self.ln(2)

    def add_title(self, title):
        self.set_fill_color(220, 220, 220)  # cinza claro
        self.set_draw_color(180, 180, 180)  # contorno cinza médio
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 0, 0)  # cor do texto (preto)

        # título com borda, fundo e centralizado
        self.cell(190, 10, title, border=1, ln=1, align="C", fill=True)
        self.ln(8)

    def add_section_title(self, section):
        self.ln(5)
        self.set_fill_color(220, 220, 220)  # cinza claro
        self.set_draw_color(180, 180, 180)  # contorno cinza médio
        self.set_font("Arial", "B", 12)
        self.cell(105, 10, section, ln=True, border=1, align="l", fill=True)
        self.ln(3)

    def add_paragraph(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 8, text.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(3)

    def add_table_metodologia(self):
        self.set_font('Arial', 'B', 11)
        self.cell(60, 8, 'Instrumento', border=1, align='C')
        self.cell(80, 8, 'Objetivo', border=1, align='C')
        self.cell(30, 8, 'No.Perguntas', border=1, align='C')
        self.ln()
        self.set_font('Arial', '', 11)
        instrumentos = [
            ('GAD-7', 'Avaliar sintomas de ansiedade', '7'),
            ('PHQ-9', 'Avaliar sintomas de depressao', '9'),
            ('SRQ-20', 'Avaliar sofrimento psiquico', '20'),
            ('Dimensões Organizacionais', 'Avaliar clima, reconhecimento e carga', '12')
        ]
        for nome, finalidade, itens in instrumentos:
            self.cell(60, 8, nome, border=1)
            self.cell(80, 8, finalidade, border=1)
            self.cell(30, 8, itens, border=1, align='C')
            self.ln()
        self.ln(5)

    def add_table_resultados(self, medias, classificacoes):
        self.set_font('Arial', 'B', 11)
        self.cell(60, 8, 'Dimensão Avaliada', border=1, align='C')
        self.cell(40, 8, 'Resultados', border=1, align='C')
        self.cell(60, 8, 'Classificação', border=1, align='C')
        self.ln()
        self.set_font('Arial', '', 11)
        for dim, media in medias.items():
            self.cell(60, 8, dim, border=1)
            self.cell(40, 8, f"{media:.2f}", border=1, align='C')
            self.cell(60, 8, classificacoes[dim], border=1, align='C')
            self.ln()

        self.ln(10)

    def add_table_referencias(self):
        self.set_font("Arial", "B", 10)
        self.cell(60, 10, "Dimensão", border=1, align='C')
        self.cell(30, 10, "Baixo", border=1, align='C')
        self.cell(30, 10, "Moderado", border=1, align='C')
        self.cell(30, 10, "Alto", border=1, align='C', ln=True)

        self.set_font("Arial", "", 10)
        referencia = {
            "GAD-7": ["0.0 - 0.99", "1.0 - 1.99", "2.0 - 3.0"],
            "PHQ-9": ["0.0 - 0.99", "1.0 - 1.99", "2.0 - 3.0"],
            "SRQ-20": ["0.0 - 0.29", "0.3 - 0.59", "0.6 - 1.0"],
            "Apoio da Liderança": ["0.0 - 0.99", "1.0 - 1.99", "2.0 - 3.0"],
            "Clima Organizacional": ["0.0 - 0.99", "1.0 - 1.99", "2.0 - 3.0"],
            "Reconhecimento": ["0.0 - 0.99", "1.0 - 1.99", "2.0 - 3.0"],
            "Sobrecarga de Trabalho": ["0.0 - 0.99", "1.0 - 1.99", "2.0 - 3.0"],
        }

        for dim, valores in referencia.items():
            self.cell(60, 10, dim, border=1, align='C')
            for valor in valores:
                self.cell(30, 10, valor, border=1, align='C')
            self.ln()
    def add_assinatura(self):
        self.ln(30)
        self.set_draw_color(0, 0, 0)
        self.line(60, self.get_y(), 150, self.get_y())  # linha horizontal

        self.ln(4)
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Responsável Técnico: Eloise Tancredi Nicoletti", ln=True, align="C")
        self.cell(0, 5, "CPF: 142.554.168-26", ln=True, align="C")

def converter_respostas(df_raw):
    mapa_freq = {"0-Nenhum dia": 0, "1-Em alguns dias": 1, "2-Mais da metade dos dias": 2, "3-Quase todos os dias": 3}
    mapa_binario = {"0 - Não": 0, "1 - Sim": 1}
    df_convertido = df_raw.copy()
    blocos_frequencia = list(range(6, 13)) + list(range(13, 22)) + list(range(42, 58))
    bloco_binario = list(range(22, 42))
    for i in blocos_frequencia:
        df_convertido.iloc[:, i] = df_convertido.iloc[:, i].map(mapa_freq)
    for i in bloco_binario:
        df_convertido.iloc[:, i] = df_convertido.iloc[:, i].astype(str).str.strip().map(mapa_binario)

    dados_final = pd.DataFrame()
    dados_final["Empresa"] = df_convertido.iloc[:, 1]
    dados_final["Data"] = pd.Timestamp.today().strftime("%d/%m/%Y")
    dados_final["Unidade"] = df_convertido.iloc[:, 5]
    dimensoes = {
        "GAD-7": list(range(6, 13)),
        "PHQ-9": list(range(13, 22)),
        "SRQ-20": list(range(22, 42)),
        "Apoio da Liderança": list(range(42, 46)),
        "Clima Organizacional": list(range(46, 50)),
        "Reconhecimento": list(range(50, 54)),
        "Sobrecarga de Trabalho": list(range(54, 58))
    }
    for nome, indices in dimensoes.items():
        dados_final[nome] = df_convertido.iloc[:, indices].mean(axis=1)
    return dados_final

def gerar_grafico_radar(medias, empresa):
    labels = list(medias.keys())
    valores = list(medias.values())
    valores += valores[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, valores, linewidth=2)
    ax.fill(angles, valores, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 3)
    plt.tight_layout()

    if not os.path.exists("laudos"):
        os.makedirs("laudos")
    nome_arquivo = f"laudos/{empresa}_grafico_radar.png"
    plt.savefig(nome_arquivo)
    plt.close()
    return nome_arquivo

def gerar_laudo_empresa(dados_empresa):
    empresa = dados_empresa['Empresa']

    data_avaliacao = dados_empresa['Data']
    unidade = dados_empresa['Unidade']

    medias = {
        "GAD-7": dados_empresa['GAD-7'],
        "PHQ-9": dados_empresa['PHQ-9'],
        "SRQ-20": dados_empresa['SRQ-20'],
        "Apoio da Liderança": dados_empresa['Apoio da Liderança'],
        "Clima Organizacional": dados_empresa['Clima Organizacional'],
        "Reconhecimento": dados_empresa['Reconhecimento'],
        "Sobrecarga de Trabalho": dados_empresa['Sobrecarga de Trabalho']
    }

    classificacoes = {}
    for dim, val in medias.items():
        if dim == "SRQ-20":
            if val >= 0.7:
                nivel = "Alto"
            elif val >= 0.4:
                nivel = "Moderado"
            else:
                nivel = "Baixo"
        else:
            if val >= 2:
                nivel = "Alto"
            elif val >= 1:
                nivel = "Moderado"
            else:
                nivel = "Baixo"
        classificacoes[dim] = nivel

    grafico_path = gerar_grafico_radar(medias, empresa.replace(" ", "_"))

    pdf = LaudoNR1()



    pdf.add_page()
    pdf.add_title("Laudo Técnico - Avaliação de Riscos Psicosociais (NR-1)")
    pdf.add_section_title("1. Identificação da Empresa")
    pdf.add_paragraph(f"Empresa: {empresa}\nData da Avaliacao: {data_avaliacao}\nUnidade Avaliada: {unidade}")
    pdf.add_section_title("2. Objetivo do Laudo")
    pdf.add_paragraph("O presente laudo visa identificar e classificar riscos psicosociais no ambiente de trabalho, em conformidade com a NR-1, proporcionando subsidios para a promoção da saúde mental organizacional.")
    pdf.add_section_title("3. Metodologia Utilizada")
    pdf.add_table_metodologia()

    pdf.add_page()
    pdf.add_section_title("4. Resultados Consolidados da Empresa")
    pdf.add_table_resultados(medias, classificacoes)
    pdf.add_section_title("4.1 Tabela de Referência de Risco por Dimensão")
    pdf.add_table_referencias()
    pdf.add_page()
    pdf.add_section_title("4.2 Grafico Radar - Dimensões Avaliadas")
    # Força espaço antes do gráfico, mas mantém na mesma página
    pdf.ln(2)
    pdf.image(grafico_path, x=30, w=150)
    # pdf.ln(5)

    pdf.add_page()
    pdf.add_section_title("5. Analise Conclusiva")
    pdf.add_interpretacao_automatica(classificacoes)
    pdf.add_page()
  # pdf.add_paragraph("Os resultados indicam níveis moderados à elevados de ansiedade, depressão e sofrimento psiquico entre os colaboradores, com destaque para sobrecarga de trabalho elevada.")
    pdf.add_section_title("6. Recomendações da Consultoria")
    pdf.add_paragraph("- Implantar campanhas de bem-estar e saúde mental;\n- Capacitar a liderança através de treinamentos voltados à Gestão de Pessoas;\n- Redefinir metas e prazos por função;\n- Criar canal sigiloso de denúncias; \n- Implantar ações de reconhecimento e meritocracia.")
    pdf.add_section_title("7. Considerações Finais")
    pdf.add_paragraph("Este laudo visa atender às exigências da NR-1 no contexto do Gerenciamento de Riscos Psicosociais, sem carater de diagnóstico clínico individual.")
    pdf.add_paragraph("Recomendamos capacitar a liderança para identificar os casos críticos individuais, com o objetivo de atuar assertivamente, de forma corretiva e preventiva.")
    pdf.add_paragraph("Estaremos à disposição da empresa, para implantar as ações que podem evitar substancialmente os casos críticos, lembrando que:")
    pdf.add_section_title("SOMENTE PESSOAS FELIZES DÃO RESULTADOS")
    pdf.add_assinatura()
    output_path = f"laudos/Laudo_{empresa.replace(' ', '_')}.pdf"
    pdf.output(output_path)


def main():
    if not os.path.exists("NR-1 2025.xlsx"):
        raise FileNotFoundError("Arquivo NR-1 2025.xlsx não encontrado.")
    df_raw = pd.read_excel("NR-1 2025.xlsx")
    dados_final = converter_respostas(df_raw)
    dados_final.to_excel("respostas_funcionarios.xlsx", sheet_name="Respostas", index=False)
    for _, row in dados_final.iterrows():
        gerar_laudo_empresa(row)
    print("Processamento completo: respostas + laudos gerados com sucesso.")



if __name__ == "__main__":
    main()
