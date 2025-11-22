import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def carregar_medias_csv(arquivo):
    """Carrega o CSV de médias em um DataFrame pandas."""
    return pd.read_csv(arquivo)

# Esta funcao gera um grafico de barras comparando a latencia media em diferentes cenarios entre o NGINX e o APACHE
def plot_latencia_media(df_nginx, df_apache, arquivo_saida="../../graficos/latencia_media.png"):
    # garantir que a pasta existe
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    cenarios_nginx = df_nginx["cenario"].unique()
    cenarios_apache = df_apache["cenario"].unique()
    
    cenarios = []
    for cenario in cenarios_nginx:
        if cenario in cenarios_apache:
            cenarios.append(cenario)
    
    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["latencia_media"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["latencia_media"].values

    x = np.arange(len(cenarios))
    largura = 0.35  

    fig, ax = plt.subplots(figsize=(12, 6))
    barras_nginx = ax.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="purple")
    barras_apache = ax.bar(x + largura/2, apache_vals, largura, label="APACHE", color="deepskyblue")

    # títulos e labels
    ax.set_ylabel("Latência Média (ms)")
    ax.set_title("Análise Comparativa de Latência Média por Cenário: NGINX vs APACHE")
    ax.set_xticks(x, cenarios, rotation=45, ha='right', fontsize=8)
    ax.legend(loc='lower right')

    ax.bar_label(barras_nginx, padding=3, fmt="%.2f", fontsize=7.5)
    ax.bar_label(barras_apache, padding=3, fmt="%.2f", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(arquivo_saida) 
    plt.close()

# Esta funcao gera um grafico de barras comparando o uso da CPU em diferentes cenarios entre o NGINX e o APACHE
def plot_cpu_media(df_nginx, df_apache, arquivo_saida="../../graficos//cpu.png"):

    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    cenarios_nginx = df_nginx["cenario"].unique()
    cenarios_apache = df_apache["cenario"].unique()
    
    cenarios = []
    for cenario in cenarios_nginx:
        if cenario in cenarios_apache:
            cenarios.append(cenario)
            
    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["cpu"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["cpu"].values

    x = np.arange(len(cenarios))
    largura = 0.35 

    fig, ax = plt.subplots(figsize=(12, 6))
    barras_nginx = ax.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="purple")
    barras_apache = ax.bar(x + largura/2, apache_vals, largura, label="APACHE", color="deepskyblue")

    ax.set_ylabel("Utilização de CPU (%)")
    ax.set_title("Análise Comparativa de Consumo de CPU por Cenário: NGINX vs APACHE")
    ax.set_xticks(x, cenarios, rotation=45, ha='right', fontsize=8)
    ax.legend(loc='lower right')

    ax.bar_label(barras_nginx, padding=3, fmt="%.2f", fontsize=7.5)
    ax.bar_label(barras_apache, padding=3, fmt="%.2f", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(arquivo_saida)  
    plt.close()

# Esta funcao gera um grafico de barras comparando o tempo medio em diferentes cenarios entre o NGINX e o APACHE
def plot_tempo_medio(df_nginx, df_apache, arquivo_saida="../../graficos//cpu.png"):
    
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    cenarios_nginx = df_nginx["cenario"].unique()
    cenarios_apache = df_apache["cenario"].unique()
    
    cenarios = []
    for cenario in cenarios_nginx:
        if cenario in cenarios_apache:
            cenarios.append(cenario)

    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["tempo_total"].values * 1000
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["tempo_total"].values * 1000

    x = np.arange(len(cenarios))
    largura = 0.35 

    fig, ax = plt.subplots(figsize=(12, 6))
    barras_nginx = ax.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="purple")
    barras_apache = ax.bar(x + largura/2, apache_vals, largura, label="APACHE", color="deepskyblue")

    ax.set_ylabel("Tempo de Resposta (ms)")
    ax.set_title("Análise Comparativa de Tempo de Resposta por Cenário: NGINX vs APACHE")
    ax.set_xticks(x, cenarios, rotation=45, ha='right', fontsize=8)
    ax.legend(loc='lower right')

    ax.bar_label(barras_nginx, padding=3, fmt="%.2f", fontsize=7.5)
    ax.bar_label(barras_apache, padding=3, fmt="%.2f", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(arquivo_saida)
    plt.close()
    
# Esta funcao gera um grafico de barras comparando a taxa de requisicoes por segundos em diferentes cenarios entre o NGINX e o APACHE
def plot_rps_media(df_nginx, df_apache, arquivo_saida="../../graficos//rps.png"):
    
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    cenarios_nginx = df_nginx["cenario"].unique()
    cenarios_apache = df_apache["cenario"].unique()
    
    cenarios = []
    for cenario in cenarios_nginx:
        if cenario in cenarios_apache:
            cenarios.append(cenario)

    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["rps"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["rps"].values

    x = np.arange(len(cenarios))
    largura = 0.35  

    fig, ax = plt.subplots(figsize=(12, 6))
    barras_nginx = ax.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="purple")
    barras_apache = ax.bar(x + largura/2, apache_vals, largura, label="APACHE", color="deepskyblue")


    ax.set_ylabel("Requisições por Segundo (RPS)")
    ax.set_title("Análise Comparativa de Requisição Média por Segundo por Cenário: NGINX vs APACHE")
    ax.set_xticks(x, cenarios, rotation=45, ha='right', fontsize=8)
    ax.legend(loc='lower right')

    ax.bar_label(barras_nginx, padding=3, fmt="%.2f", fontsize=7.5)
    ax.bar_label(barras_apache, padding=3, fmt="%.2f", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(arquivo_saida)  
    plt.close()

# Esta funcao gera um grafico de barras comparando o uso de Memoria em diferentes cenarios entre o NGINX e o APACHE
def plot_memoria_media(df_nginx, df_apache, arquivo_saida="../../graficos//memoria.png"):
    
    os.makedirs(os.path.dirname(arquivo_saida) or ".", exist_ok=True)

    cenarios_nginx = df_nginx["cenario"].unique()
    cenarios_apache = df_apache["cenario"].unique()
    
    cenarios = []
    for cenario in cenarios_nginx:
        if cenario in cenarios_apache:
            cenarios.append(cenario)

    nginx_vals = df_nginx.set_index("cenario").loc[cenarios]["memoria"].values
    apache_vals = df_apache.set_index("cenario").loc[cenarios]["memoria"].values

    x = np.arange(len(cenarios))
    largura = 0.35  

    fig, ax = plt.subplots(figsize=(12, 6))
    barras_nginx = ax.bar(x - largura/2, nginx_vals, largura, label="NGINX", color="purple")
    barras_apache = ax.bar(x + largura/2, apache_vals, largura, label="APACHE", color="deepskyblue")


    ax.set_ylabel("Utilização de Memória (%)")
    ax.set_title("Análise Comparativa de Consumo de Memória por Cenário: NGINX vs APACHE")
    ax.set_xticks(x, cenarios, rotation=45, ha='right', fontsize=8)
    ax.legend(loc='lower right')

    ax.bar_label(barras_nginx, padding=3, fmt="%.2f", fontsize=7.5)
    ax.bar_label(barras_apache, padding=3, fmt="%.2f", fontsize=7.5)

    plt.tight_layout()
    plt.savefig(arquivo_saida)  
    plt.close()

