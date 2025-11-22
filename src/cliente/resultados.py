import numpy as np
import time
import csv
from concurrent.futures import as_completed, ThreadPoolExecutor
from cliente import Cliente
import requests
import os
import numpy as np
import statistics
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
                    medias[cenario][chave] = statistics.mean(valores)
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

def carregar_medias_csv(arquivo):
    """Carrega o CSV de médias em um DataFrame pandas."""
    return pd.read_csv(arquivo)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def carregar_medias_csv(arquivo):
    """Carrega o CSV de médias em um DataFrame pandas."""
    return pd.read_csv(arquivo)

def plot_latencia_media(df_nginx, df_apache, arquivo_saida="resultados/latencia_media.png"):
    """
    Gera e salva um gráfico de barras comparando a latência média
    entre NGINX e APACHE para todos os cenários.
    """
    # garantir que a pasta existe
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    # garantir que os cenários sejam os mesmos nos dois DataFrames
    cenarios = sorted(set(df_nginx["cenario"]).intersection(df_apache["cenario"]))

    # extrair valores de latência média
    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["latencia_media"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["latencia_media"].values

    x = np.arange(len(cenarios))
    largura = 0.35  # largura das barras

    plt.figure(figsize=(12, 6))
    plt.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="steelblue")
    plt.bar(x + largura/2, apache_vals, largura, label="APACHE", color="darkorange")

    # títulos e labels
    plt.ylabel("Latência Média (ms)")
    plt.title("Comparação de Latência Média por Cenário (NGINX vs APACHE)")
    plt.xticks(x, cenarios, rotation=45)
    plt.legend()

    # adiciona valores numéricos acima das barras
    for i, v in enumerate(nginx_vals):
        plt.text(i - largura/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    for i, v in enumerate(apache_vals):
        plt.text(i + largura/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(arquivo_saida)   # salva na pasta resultados
    plt.close()

def plot_cpu_media(df_nginx, df_apache, arquivo_saida="resultados/cpu.png"):
    """
    Gera e salva um gráfico de barras comparando a latência média
    entre NGINX e APACHE para todos os cenários.
    """
    # garantir que a pasta existe
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    # garantir que os cenários sejam os mesmos nos dois DataFrames
    cenarios = sorted(set(df_nginx["cenario"]).intersection(df_apache["cenario"]))

    # extrair valores de latência média
    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["cpu"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["cpu"].values

    x = np.arange(len(cenarios))
    largura = 0.35  # largura das barras

    plt.figure(figsize=(12, 6))
    plt.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="steelblue")
    plt.bar(x + largura/2, apache_vals, largura, label="APACHE", color="darkorange")

    # títulos e labels
    plt.ylabel("CPU")
    plt.title("Comparação de CPU Média por Cenário (NGINX vs APACHE)")
    plt.xticks(x, cenarios, rotation=45)
    plt.legend()

    # adiciona valores numéricos acima das barras
    for i, v in enumerate(nginx_vals):
        plt.text(i - largura/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    for i, v in enumerate(apache_vals):
        plt.text(i + largura/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(arquivo_saida)   # salva na pasta resultados
    plt.close()

def plot_tempo_medio(df_nginx, df_apache, arquivo_saida="resultados/cpu.png"):
    """
    Gera e salva um gráfico de barras comparando a latência média
    entre NGINX e APACHE para todos os cenários.
    """
    # garantir que a pasta existe
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    # garantir que os cenários sejam os mesmos nos dois DataFrames
    cenarios = sorted(set(df_nginx["cenario"]).intersection(df_apache["cenario"]))

    # extrair valores de latência média
    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["tempo_total"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["tempo_total"].values

    x = np.arange(len(cenarios))
    largura = 0.35  # largura das barras

    plt.figure(figsize=(12, 6))
    plt.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="steelblue")
    plt.bar(x + largura/2, apache_vals, largura, label="APACHE", color="darkorange")

    # títulos e labels
    plt.ylabel("tempo_total")
    plt.title("Comparação de tempo_total Média por Cenário (NGINX vs APACHE)")
    plt.xticks(x, cenarios, rotation=45)
    plt.legend()

    # adiciona valores numéricos acima das barras
    for i, v in enumerate(nginx_vals):
        plt.text(i - largura/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    for i, v in enumerate(apache_vals):
        plt.text(i + largura/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(arquivo_saida)   # salva na pasta resultados
    plt.close()

def scatter_cpu_vs_latencia(df_nginx, df_apache, arquivo_saida="resultados/scatter_cpu_latencia.png"):
    """Gráfico conjunto CPU vs Latência Média para NGINX e Apache."""
    plt.figure(figsize=(8,6))
    plt.scatter(df_nginx["cpu"], df_nginx["latencia_media"], color="steelblue", label="NGINX", alpha=0.7)
    plt.scatter(df_apache["cpu"], df_apache["latencia_media"], color="darkorange", label="Apache", alpha=0.7)
    plt.xlabel("CPU (%)")
    plt.ylabel("Latência Média (ms)")
    plt.title("CPU vs Latência Média (NGINX vs Apache)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(arquivo_saida)
    plt.close()


def scatter_threads_vs_rps(df_nginx, df_apache, arquivo_saida="resultados/scatter_threads_rps.png"):
    """Gráfico conjunto Threads vs RPS para NGINX e Apache."""
    df_nginx["threads"] = df_nginx["cenario"].str.extract(r"threads=(\d+)").astype(int)
    df_apache["threads"] = df_apache["cenario"].str.extract(r"threads=(\d+)").astype(int)

    plt.figure(figsize=(8,6))
    plt.scatter(df_nginx["threads"], df_nginx["rps"], color="steelblue", label="NGINX", alpha=0.7)
    plt.scatter(df_apache["threads"], df_apache["rps"], color="darkorange", label="Apache", alpha=0.7)
    plt.xlabel("Número de Threads")
    plt.ylabel("RPS")
    plt.title("Threads vs RPS (NGINX vs Apache)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(arquivo_saida)
    plt.close()

