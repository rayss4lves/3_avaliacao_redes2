import time
from concurrent.futures import as_completed, ThreadPoolExecutor
from cliente import Cliente
import requests
from gerar_csvs import calcular_medias_por_cenario, salvar_execucoes_csv, salvar_medias_csv
from gerar_graficos import carregar_medias_csv,plot_latencia_media, plot_cpu_media, plot_tempo_medio, plot_rps_media, plot_memoria_media

NUMERO_REQUISICOES = 200
NUM_EXECUCOES = 20
PROMETHEUS_URL = "http://prometheus:9090"

def consultar_prometheus(prometheus_url, query):
    resultado = None
    try:
        resp = requests.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("data", {}).get("result", [])
            resultado = result
    except Exception as e:
        print("Erro ao consultar Prometheus:", e)
        
    return resultado

def coletar_cpu(servidor):
    if servidor == "nginx":
        instance="95.58.0.2:9100"
    else:
        instance="95.58.0.4:9100"
    query = f'100 - (avg(rate(node_cpu_seconds_total{{mode="idle", instance="{instance}"}}[5m])) * 100)'
    return consultar_prometheus(PROMETHEUS_URL, query)

def coletar_memoria(servidor):
    if servidor == "nginx":
        instance="95.58.0.2:9100"
    else:
        instance="95.58.0.4:9100"
    query = (
        f'(1 - (node_memory_MemAvailable_bytes{{instance="{instance}"}} / '
        f'node_memory_MemTotal_bytes{{instance="{instance}"}})) * 100'
    )
    return consultar_prometheus(PROMETHEUS_URL, query)

def coletar_metricas_prometheus(nome):
    cpu = coletar_cpu(nome)
    memoria = coletar_memoria(nome)
    if cpu and len(cpu) > 0:
        cpu = float(cpu[0]['value'][1])
    else:
        cpu = 0.0
    if memoria and len(memoria) > 0:
        memoria = float(memoria[0]['value'][1])
    else:
        memoria = 0.0
        
    return cpu, memoria

def executar_requisicao(host, porta, caminho):
    resultado_dict = {}
    try:
        cliente = Cliente(host, porta)
        resultado = cliente.enviar_requisicao("GET", caminho)
        resultado_dict = {
            'servidor': host,
            'sucesso': resultado.get('sucesso', False),
            'tempo_total': resultado.get('tempo_total', 0),
            'codigo_status': resultado.get('codigo_status', 0)
        }
    except Exception as e:
        print(f"Erro ao executar requisicao: {e}")
        resultado_dict = {
            'servidor': host,
            'sucesso': False,
            'tempo_total': 0,
            'codigo_status': 0
        }
    return resultado_dict

def stress(servidor, host, porta, caminho, execucao):
    resultados = []
    tempo_inicio = time.time()
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for _ in range(NUMERO_REQUISICOES):
            future = executor.submit(executar_requisicao, host, porta, caminho)
            futures.append(future)
        
        for futuro in as_completed(futures):
            try:
                resultado = futuro.result()
                resultados.append(resultado)
            except Exception as e:
                print("Erro na requisicao:", e)
                resultados.append({
                    "sucesso": False,
                    "tempo_total": 0,
                    "codigo_status": 0
                })
    
    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    
    # METRICAS
    sucessos = 0
    
    for r in resultados:
        if r.get('sucesso', False):
            sucessos += 1

    falhas = len(resultados) - sucessos 
    
    tempos = []
    for r in resultados:
        if r.get('sucesso', False) and r.get('tempo_total', 0) > 0:
            tempos.append(r['tempo_total'] * 1000)
        

    cpu, memoria = coletar_metricas_prometheus(servidor)
    
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
        "memoria": memoria,
        "latencia_media": latencia_media,
        "rps": rps,
        "latencia_min": latencia_min,
        "latencia_max": latencia_max
    }

if __name__ == "__main__":
    
    CENARIOS = [
            { "caminho": "/arquivo_10kb.txt", "threads": 5 },
            { "caminho": "/arquivo_10kb.txt", "threads": 10 },
            { "caminho": "/arquivo_10kb.txt", "threads": 15 },
            
            { "caminho": "/arquivo_1mb.txt", "threads": 5 },
            { "caminho": "/arquivo_1mb.txt", "threads": 10 },
            { "caminho": "/arquivo_1mb.txt", "threads": 15 },
            
            { "caminho": "/arquivo_10mb.txt", "threads": 5 },
            { "caminho": "/arquivo_10mb.txt", "threads": 10 },
            { "caminho": "/arquivo_10mb.txt", "threads": 15 },
        ]


    resultados_nginx = {}
    resultados_apache = {}
    
    print("======= Testes NGINX - APACHE =======")
    for cenario in CENARIOS:
        chave = f"{cenario['caminho']}|threads={cenario['threads']}"
        print(f"Coletando metricas - {chave}")
        resultados_nginx[chave] = []
        resultados_apache[chave] = []
        for i in range(NUM_EXECUCOES):
            NUM_THREADS = cenario["threads"]
            nginx = stress("nginx", "95.58.0.2", 80, cenario["caminho"], i)
            resultados_nginx[chave].append(nginx)
            
            apache = stress("apache", "95.58.0.4", 80, cenario["caminho"], i)
            resultados_apache[chave].append(apache)
                        
    # salvar resultados
    medias_nginx = calcular_medias_por_cenario(resultados_nginx)
    medias_apache = calcular_medias_por_cenario(resultados_apache)
    
    salvar_medias_csv(medias_nginx, arquivo="resultados/nginx_medias_prometheus.csv")
    salvar_medias_csv(medias_apache, arquivo="resultados/apache_medias_prometheus.csv")

    salvar_execucoes_csv(resultados_nginx, arquivo="resultados/nginx_metricas_prometheus.csv")
    salvar_execucoes_csv(resultados_apache, arquivo="resultados/apache_metricas_prometheus.csv")

    #gerar graficos

    df_nginx = carregar_medias_csv("resultados/nginx_medias_prometheus.csv")
    df_apache = carregar_medias_csv("resultados/apache_medias_prometheus.csv")

    plot_latencia_media(df_nginx, df_apache, arquivo_saida="../../graficos//latencia_media.png")
    plot_cpu_media(df_nginx, df_apache, arquivo_saida="../../graficos//cpu.png")
    plot_tempo_medio(df_nginx, df_apache, arquivo_saida="../../graficos//tempo_total.png")
    plot_rps_media(df_nginx, df_apache, arquivo_saida="../../graficos//rps.png")
    plot_memoria_media(df_nginx, df_apache, arquivo_saida="../../graficos//memoria.png")