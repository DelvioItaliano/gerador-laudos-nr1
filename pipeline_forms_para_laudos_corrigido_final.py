import matplotlib.pyplot as plt

def gerar_grafico_exemplo():
    categorias = ['Ansiedade', 'Depressão', 'Estresse']
    valores = [5, 7, 3]
    plt.bar(categorias, valores)
    plt.title("Exemplo de gráfico NR1")
    plt.savefig("grafico.png")

if __name__ == "__main__":
    gerar_grafico_exemplo()
