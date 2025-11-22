import numpy as np
import csv
import os
from datetime import datetime


def calcular_medias_por_cenario(resultados):
    campos_ignorar = {"Execucao", "total_requisicoes", "numero_threads"}
    medias = {}
    for cenario, execucoes in resultados.items():
        medias[cenario] = {}
        # pega todas as chaves numéricas
        for chave in execucoes[0].keys():
            if chave not in campos_ignorar:
                valores = [e[chave] for e in execucoes if isinstance(e[chave], (int, float))]
                if valores:  # só calcula se houver números
                    medias[cenario][chave] = np.mean(valores)
    return medias

def salvar_execucoes_csv(resultados, arquivo="resultados/metricas_prometheus.csv"):
    # resultados é um dict: { "cenario": [ {execução}, {execução}, ... ] }
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = None
        for cenario, execucoes in resultados.items():
            for execucao in execucoes:
                # inicializa o writer só uma vez, com as chaves + campo 'cenario'
                if writer is None:
                    campos = ["timestamp", "cenario"] + list(execucao.keys())
                    writer = csv.DictWriter(f, fieldnames=campos)
                    writer.writeheader()
                linha = dict(execucao)
                linha["timestamp"] = timestamp
                linha["cenario"] = cenario
                writer.writerow(linha)

def salvar_medias_csv(medias, arquivo="resultados/medias.csv"):
    # Garante que o diretório existe
    os.makedirs(os.path.dirname(arquivo) or ".", exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Pega os campos do primeiro cenário + adiciona 'cenario'
    primeiro_cenario = next(iter(medias))
    campos = ["timestamp", "cenario"] + list(medias[primeiro_cenario].keys())

    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

        for cenario, metricas in medias.items():
            linha = dict(metricas)
            linha["timestamp"] = timestamp
            linha["cenario"] = cenario
            writer.writerow(linha)

