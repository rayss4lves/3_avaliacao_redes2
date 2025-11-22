import time
import csv
from concurrent.futures import as_completed, ThreadPoolExecutor
from cliente import Cliente
import requests
import os
import numpy as np
from resultados import calcular_medias_por_cenario, salvar_execucoes_csv, salvar_medias_csv, carregar_medias_csv,plot_latencia_media, plot_cpu_media, plot_tempo_medio

NUMERO_REQUISICOES = 2000
NUM_EXECUCOES = 4

def consultar_prometheus(prometheus_url, query):
    try:
        resp = requests.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", {}).get("result", [])
            return result
    except Exception as e:
        print("Erro ao consultar Prometheus:", e)
        return None

PROMETHEUS_URL = "http://prometheus:9090"

def coletar_cpu(servidor):
    if servidor == "nginx":
        query = 'sum(rate(node_cpu_seconds_total{instance="95.58.0.2:9100", mode!="idle"}[30s]))'
    else:
        query = 'sum(rate(node_cpu_seconds_total{instance="95.58.0.4:9100", mode!="idle"}[30s]))'
    return consultar_prometheus(PROMETHEUS_URL, query)


def coletar_metricas_prometheus(nome):
    cpu = coletar_cpu(nome)
    
    if cpu and len(cpu) > 0:
        cpu = float(cpu[0]['value'][1])
    else:
        cpu = 0.0
    return cpu

def executar_requisicao(host, porta, caminho):
    try:
        cliente = Cliente(host, porta)
        resultado = cliente.enviar_requisicao("GET", caminho)
        return {
            'servidor': host,
            'sucesso': resultado.get('sucesso', False),
            'tempo_total': resultado.get('tempo_total', 0),
            'codigo_status': resultado.get('codigo_status', 0)
        }
    except Exception as e:
        print(f"Erro ao executar requisição: {e}")
        return {
            'servidor': host,
            'sucesso': False,
            'tempo_total': 0,
            'codigo_status': 0
        }

def stress(servidor, host, porta, caminho, execucao):
    resultados = []
    tempo_inicio = time.time()
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [
            executor.submit(executar_requisicao, host, porta, caminho)
            for _ in range(NUMERO_REQUISICOES)
        ]
        
        for futuro in as_completed(futures):
            try:
                resultado = futuro.result()
                resultados.append(resultado)
            except Exception as e:
                print("Erro na requisição:", e)
                resultados.append({
                    "sucesso": False,
                    "tempo_total": 0,
                    "codigo_status": 0
                })
    
    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    
    # METRICAS
    sucessos = sum(1 for r in resultados if r.get('sucesso', False))
    falhas = len(resultados) - sucessos 
    
    tempos = [r['tempo_total'] * 1000 for r in resultados 
              if r.get('sucesso', False) and r.get('tempo_total', 0) > 0]
    
    cpu = coletar_metricas_prometheus(servidor)
    
    if tempos:
        latencia_media = sum(tempos) / len(tempos)
        rps = len(tempos) / tempo_total
        latencia_min = min(tempos)
        latencia_max = max(tempos)
    else:
        latencia_media = 0
        rps = 0
        latencia_min = 0
        latencia_max = 0
    
    return {
        "servidor": servidor,
        "caminho": caminho,
        "Execucao": execucao,
        "total_requisicoes": NUMERO_REQUISICOES,
        "numero_threads": NUM_THREADS,
        "sucesso": sucessos,
        "erros": falhas,
        "tempo_total": tempo_total,
        "cpu": cpu,
        "latencia_media": latencia_media,
        "rps": rps,
        "latencia_min": latencia_min,
        "latencia_max": latencia_max
    }



if __name__ == "__main__":
    CENARIOS = [
        { "caminho": "/arquivo_10kb.txt", "threads": 2 },
        { "caminho": "/arquivo_10kb.txt", "threads": 10 },
        { "caminho": "/arquivo_10kb.txt", "threads": 50 },

        { "caminho": "/arquivo_1mb.txt", "threads": 2 },
        { "caminho": "/arquivo_1mb.txt", "threads": 10 },
        { "caminho": "/arquivo_1mb.txt", "threads": 50 },

        { "caminho": "/arquivo_10mb.txt", "threads": 2 },
        { "caminho": "/arquivo_10mb.txt", "threads": 10 },
        { "caminho": "/arquivo_10mb.txt", "threads": 50 },
    ]


    resultados_nginx = {}
    resultados_apache = {}
    print("=== Testes NGINX ===")
    for cenario in CENARIOS:
        chave = f"{cenario['caminho']}|threads={cenario['threads']}"
        resultados_nginx[chave] = []
        for i in range(NUM_EXECUCOES):
            print(f"Coletando métricas para NGINX - {chave}")
            NUM_THREADS = cenario["threads"]
            nginx = stress("nginx", "95.58.0.2", 80, cenario["caminho"], i)
            resultados_nginx[chave].append(nginx)


   
    print("\n=== Testes Apache ===")
    for cenario in CENARIOS:
        chave = f"{cenario['caminho']}|threads={cenario['threads']}"
        resultados_apache[chave] = []
        for i in range(NUM_EXECUCOES):
            print(f"Coletando métricas para Apache - {chave}")
            NUM_THREADS = cenario["threads"]
            apache = stress("apache", "95.58.0.4", 80, cenario["caminho"], i)
            resultados_apache[chave].append(apache)


    medias_nginx = calcular_medias_por_cenario(resultados_nginx)
    medias_apache = calcular_medias_por_cenario(resultados_apache)
    
    salvar_medias_csv(medias_nginx, arquivo="resultados/nginx_medias_prometheus.csv")
    salvar_medias_csv(medias_apache, arquivo="resultados/apache_medias_prometheus.csv")

    salvar_execucoes_csv(resultados_nginx, arquivo="resultados/nginx_metricas_prometheus.csv")
    salvar_execucoes_csv(resultados_apache, arquivo="resultados/apache_metricas_prometheus.csv")

    df_nginx = carregar_medias_csv("resultados/nginx_medias_prometheus.csv")
    df_apache = carregar_medias_csv("resultados/apache_medias_prometheus.csv")

    plot_latencia_media(df_nginx, df_apache, arquivo_saida="resultados/latencia_media.png")
    plot_cpu_media(df_nginx, df_apache, arquivo_saida="resultados/cpu.png")
    plot_tempo_medio(df_nginx, df_apache, arquivo_saida="resultados/tempo_total.png")
