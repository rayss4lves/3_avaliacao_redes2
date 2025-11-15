import time
import csv
import concurrent.futures
import threading
from cliente.cliente import Cliente
import requests
import os

def consultar_prometheus(prometheus_url, query):
    try:
        resp = requests.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        data = resp.json()
        return data["data"]["result"]
    except Exception as e:
        print("Erro ao consultar Prometheus:", e)
        return None


PROMETHEUS_URL = "http://95.58.0.6:9090"   # Ajuste para o IP do Prometheus


def executar_requisicao(host, porta, caminho):
    cliente = Cliente(host, porta)
    sucesso, tempo, status, _ = cliente.enviar_requisicao("GET", caminho)
    return sucesso


def stress(host, porta, caminho, total, concorrencia):
    with concurrent.futures.ThreadPoolExecutor(max_workers=concorrencia) as executor:
        futures = [
            executor.submit(executar_requisicao, host, porta, caminho)
            for _ in range(total)
        ]
        resultados = [f.result() for f in concurrent.futures.as_completed(futures)]

    return resultados.count(True), resultados.count(False)


def coletar_metricas_nginx():
    return {
        "req_total": consultar_prometheus(PROMETHEUS_URL, "nginx_http_requests_total"),
        "latencia_sum": consultar_prometheus(PROMETHEUS_URL, "nginx_http_requests_duration_seconds_sum"),
        "latencia_count": consultar_prometheus(PROMETHEUS_URL, "nginx_http_requests_duration_seconds_count")
    }


def coletar_metricas_apache():
    return {
        "req_total": consultar_prometheus(PROMETHEUS_URL, "apache_accesses_total"),
        "conexoes": consultar_prometheus(PROMETHEUS_URL, "apache_connections_total"),
        "cpu_user": consultar_prometheus(PROMETHEUS_URL, "apache_cpu_user_seconds_total")
    }


def executar_teste_prometheus(nome, host, porta, caminho="/", total=200, concorrencia=20):
    print(f"\n===== TESTE {nome.upper()} =====")

    # Metricas antes
    if nome == "nginx":
        antes = coletar_metricas_nginx()
    else:
        antes = coletar_metricas_apache()

    # Executa o stress
    sucesso, erros = stress(host, porta, caminho, total, concorrencia)
    print(f"Sucesso: {sucesso} | Erros: {erros}")

    # Metricas depois
    if nome == "nginx":
        depois = coletar_metricas_nginx()
    else:
        depois = coletar_metricas_apache()

    return {
        "servidor": nome,
        "sucesso": sucesso,
        "erros": erros,
        "metricas_antes": antes,
        "metricas_depois": depois
    }


def salvar_execucoes_csv(resultados, nome_servidor, arquivo="resultados/metricas_prometheus.csv"):
    os.makedirs(os.path.dirname(arquivo) if os.path.dirname(arquivo) else '.', exist_ok=True)
    with open("metricas_prometheus.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["servidor", "sucesso", "erros", "metricas_antes", "metricas_depois"])

        for r in resultados:
            writer.writerow([
                r["servidor"],
                r["sucesso"],
                r["erros"],
                r["metricas_antes"],
                r["metricas_depois"]
            ])


if __name__ == "__main__":
    
    CENARIOS = [
        ("/arquivo_5kb.txt", 200, 20),
        ("/arquivo_500kb.txt", 200, 20),
        ("/arquivo_5mb.txt", 100, 10),
]

    resultados = []

    # Testes NGINX
    for caminho, total, concorrencia in CENARIOS:
        nginx = executar_teste_prometheus("nginx", "54.99.0.10", 80, caminho, total, concorrencia)
        resultados.append(nginx)

    # Testes Apache
    for caminho, total, concorrencia in CENARIOS:
        apache = executar_teste_prometheus("apache", "54.99.0.11", 80, caminho, total, concorrencia)
        resultados.append(apache)

    salvar_csv(resultados)
    print("\nMetricas salvas em metricas_prometheus.csv")

    nginx = executar_teste_prometheus("nginx", "54.99.0.10", 80)
    apache = executar_teste_prometheus("apache", "54.99.0.11", 80)

    salvar_csv([nginx, apache])

    print("\nMetricas salvas em metricas_prometheus.csv")
