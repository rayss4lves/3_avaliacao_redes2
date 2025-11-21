import time
import csv
from concurrent.futures import as_completed, ThreadPoolExecutor
from cliente import Cliente
import requests
import os

NUM_THREADS = 2
NUMERO_REQUISICOES = 200

def consultar_prometheus(prometheus_url, query):
    try:
        resp = requests.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            print( data )
            return data["data"]["result"]
    except Exception as e:
        print("Erro ao consultar Prometheus:", e)
        return None

PROMETHEUS_URL = "http://prometheus:9090"

def coletar_cpu(servidor):
    if servidor == "nginx":
        return consultar_prometheus(PROMETHEUS_URL, 
            "rate(process_cpu_seconds_total_requisicoes{job='nginx'}[30s])")
    else:
        return consultar_prometheus(PROMETHEUS_URL, 
            "rate(process_cpu_seconds_total_requisicoes{job='apache'}[30s])")

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

def stress(servidor, host, porta, caminho):
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
    
    # CORREÇÃO 1: sucessos é int, não lista
    sucessos = sum(1 for r in resultados if r.get('sucesso', False))
    falhas = len(resultados) - sucessos  # CORRETO: subtrair int de int
    
    # CORREÇÃO 2: só pegar tempos de requisições bem-sucedidas
    tempos = [r['tempo_total'] * 1000 for r in resultados 
              if r.get('sucesso', False) and r.get('tempo_total', 0) > 0]
    
    cpu = coletar_metricas_prometheus(servidor)
    
    # CORREÇÃO 3: inicializar variáveis mesmo se tempos estiver vazio
    if tempos:
        latencia_media = sum(tempos) / len(tempos)
        rps = len(tempos) / tempo_total
    else:
        latencia_media = 0
        rps = 0
    
    return {
        "servidor": servidor,
        "caminho": caminho,
        "total_requisicoes": NUMERO_REQUISICOES,
        "numero_threads": NUM_THREADS,
        "sucesso": sucessos,
        "erros": falhas,
        "tempo_total": tempo_total,
        "cpu": cpu,
        "latencia_media": latencia_media,
        "rps": rps
    }

def salvar_execucoes_csv(dados, arquivo="resultados/metricas_prometheus.csv"):
    os.makedirs(os.path.dirname(arquivo) if os.path.dirname(arquivo) else '.', 
                exist_ok=True)
    novo_arquivo = not os.path.exists(arquivo)
    
    with open(arquivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados.keys())
        if novo_arquivo:
            writer.writeheader()
        writer.writerow(dados)

if __name__ == "__main__":
    CENARIOS = [
        "/arquivo_5kb.txt",
        "/arquivo_500kb.txt",
        "/arquivo_5mb.txt",
    ]
    
    print("=== Testes NGINX ===")
    for caminho in CENARIOS:
        print(f"Coletando metricas para NGINX - Caminho: {caminho}")
        try:
            # Porta 8080 mapeada para nginx (localhost do Windows)
            nginx = stress("nginx", "95.58.0.2", 80, caminho)
            salvar_execucoes_csv(nginx, arquivo="resultados/metricas_prometheus.csv")
        except Exception as e:
            print(f"Erro no teste NGINX: {e}")
    
    print("\n=== Testes Apache ===")
    for caminho in CENARIOS:
        print(f"Coletando metricas para Apache - Caminho: {caminho}")
        try:
            # Porta 8082 mapeada para apache (localhost do Windows)
            apache = stress("apache", "95.58.0.4", 80, caminho)
            salvar_execucoes_csv(apache, arquivo="resultados/metricas_prometheus.csv")
        except Exception as e:
            print(f"Erro no teste Apache: {e}")
    
    print("\nMetricas salvas em metricas_prometheus.csv")