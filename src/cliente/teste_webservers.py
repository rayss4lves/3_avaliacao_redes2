import socket
import hashlib
import time
import threading
import json
from datetime import datetime

# Cliente para testes contra Nginx e Apache
def gerar_hash():
    chave = '20239019558 Rayssa Alves'
    sha1_hash = hashlib.sha1(chave.encode()).hexdigest()
    return sha1_hash

X_CUSTOM_ID = gerar_hash()

class ClienteWebServers:
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta
        self.resultados = []
        self.lock = threading.Lock()
    
    def enviar_requisicao(self, metodo='GET', caminho='/', corpo=None):
        """Envia uma requisição HTTP e retorna tempo de resposta"""
        try:
            tempo_inicial = time.time()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect((self.host, self.porta))
            
            cabecalhos = [f"Host: {self.host}", f"X-Custom-ID: {X_CUSTOM_ID}", "Connection: close"]
            corpo_texto = ""
            if corpo:
                corpo_texto = str(corpo)
                cabecalhos.append(f"Content-Length: {len(corpo_texto.encode('utf-8'))}")
            
            cabecalhos_str = "\r\n".join(cabecalhos)
            request = f"{metodo} {caminho} HTTP/1.1\r\n{cabecalhos_str}\r\n\r\n"
            
            if corpo_texto:
                request += corpo_texto
            
            client_socket.sendall(request.encode())
            resposta = client_socket.recv(4096)
            tempo_final = time.time()
            
            client_socket.close()
            
            response_time = tempo_final - tempo_inicial
            success = b"200" in resposta
            
            return success, response_time, resposta.decode()
        except Exception as e:
            return False, 0, str(e)
    
    def teste_sequencial(self, num_requisicoes=100):
        """Teste sequencial contra o servidor"""
        tempos = []
        sucessos = 0
        falhas = 0
        
        print(f"Iniciando {num_requisicoes} requisições sequenciais contra {self.host}:{self.porta}")
        
        for i in range(num_requisicoes):
            success, response_time, _ = self.enviar_requisicao()
            tempos.append(response_time)
            
            if success:
                sucessos += 1
            else:
                falhas += 1
            
            if (i + 1) % 10 == 0:
                print(f"  Progresso: {i + 1}/{num_requisicoes}")
        
        return {
            'tipo': 'sequencial',
            'total_requisicoes': num_requisicoes,
            'sucessos': sucessos,
            'falhas': falhas,
            'tempos': tempos,
            'tempo_medio': sum(tempos) / len(tempos) if tempos else 0,
            'tempo_minimo': min(tempos) if tempos else 0,
            'tempo_maximo': max(tempos) if tempos else 0,
            'tempo_total': sum(tempos),
            'taxa_sucesso': (sucessos / num_requisicoes) * 100 if num_requisicoes > 0 else 0
        }
    
    def teste_concorrente(self, num_requisicoes=100, num_threads=10):
        """Teste concorrente contra o servidor"""
        self.resultados = []
        requisicoes_por_thread = num_requisicoes // num_threads
        
        print(f"Iniciando {num_requisicoes} requisições concorrentes ({num_threads} threads) contra {self.host}:{self.porta}")
        
        threads = []
        tempo_inicio = time.time()
        
        def worker():
            for _ in range(requisicoes_por_thread):
                success, response_time, _ = self.enviar_requisicao()
                with self.lock:
                    self.resultados.append({
                        'success': success,
                        'time': response_time
                    })
        
        for i in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        tempo_total = time.time() - tempo_inicio
        
        tempos = [r['time'] for r in self.resultados]
        sucessos = sum(1 for r in self.resultados if r['success'])
        falhas = len(self.resultados) - sucessos
        
        return {
            'tipo': 'concorrente',
            'total_requisicoes': len(self.resultados),
            'num_threads': num_threads,
            'sucessos': sucessos,
            'falhas': falhas,
            'tempos': tempos,
            'tempo_medio': sum(tempos) / len(tempos) if tempos else 0,
            'tempo_minimo': min(tempos) if tempos else 0,
            'tempo_maximo': max(tempos) if tempos else 0,
            'tempo_total_execucao': tempo_total,
            'taxa_sucesso': (sucessos / len(self.resultados)) * 100 if self.resultados else 0,
            'throughput': len(self.resultados) / tempo_total if tempo_total > 0 else 0
        }

def mostrar_resultado(resultado):
    """Exibe os resultados de forma formatada"""
    print("\n" + "="*60)
    print(f"Tipo de Teste: {resultado['tipo'].upper()}")
    print("="*60)
    print(f"Total de Requisições: {resultado['total_requisicoes']}")
    print(f"Sucessos: {resultado['sucessos']}")
    print(f"Falhas: {resultado['falhas']}")
    print(f"Taxa de Sucesso: {resultado['taxa_sucesso']:.2f}%")
    print(f"\nTempo Médio: {resultado['tempo_medio']:.4f}s")
    print(f"Tempo Mínimo: {resultado['tempo_minimo']:.4f}s")
    print(f"Tempo Máximo: {resultado['tempo_maximo']:.4f}s")
    print(f"Tempo Total: {resultado['tempo_total_execucao']:.2f}s" if 'tempo_total_execucao' in resultado else f"Tempo Total: {resultado['tempo_total']:.2f}s")
    
    if 'throughput' in resultado:
        print(f"Throughput: {resultado['throughput']:.2f} req/s")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTE DE PERFORMANCE - NGINX E APACHE")
    print("="*60)
    
    # Teste Nginx
    print("\n[1] TESTANDO NGINX (95.58.0.5:80)")
    cliente_nginx = ClienteWebServers('nginx', 80)
    
    resultado_nginx_seq = cliente_nginx.teste_sequencial(num_requisicoes=100)
    mostrar_resultado(resultado_nginx_seq)
    
    resultado_nginx_conc = cliente_nginx.teste_concorrente(num_requisicoes=100, num_threads=10)
    mostrar_resultado(resultado_nginx_conc)
    
    # Teste Apache
    print("\n[2] TESTANDO APACHE (95.58.0.6:80)")
    cliente_apache = ClienteWebServers('apache', 80)
    
    resultado_apache_seq = cliente_apache.teste_sequencial(num_requisicoes=100)
    mostrar_resultado(resultado_apache_seq)
    
    resultado_apache_conc = cliente_apache.teste_concorrente(num_requisicoes=100, num_threads=10)
    mostrar_resultado(resultado_apache_conc)
    
    # Comparação
    print("\n" + "="*60)
    print("COMPARAÇÃO: NGINX vs APACHE")
    print("="*60)
    print(f"\nNginx (Sequencial) - Tempo Médio: {resultado_nginx_seq['tempo_medio']:.4f}s")
    print(f"Apache (Sequencial) - Tempo Médio: {resultado_apache_seq['tempo_medio']:.4f}s")
    print(f"Diferença: {abs(resultado_nginx_seq['tempo_medio'] - resultado_apache_seq['tempo_medio']):.4f}s")
    
    print(f"\nNginx (Concorrente) - Throughput: {resultado_nginx_conc['throughput']:.2f} req/s")
    print(f"Apache (Concorrente) - Throughput: {resultado_apache_conc['throughput']:.2f} req/s")
    print(f"Nginx é {resultado_nginx_conc['throughput'] / resultado_apache_conc['throughput']:.2f}x mais rápido")
    
    # Salvar resultados em JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'/app/resultados/teste_webservers_{timestamp}.json', 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'nginx': {
                'sequencial': resultado_nginx_seq,
                'concorrente': resultado_nginx_conc
            },
            'apache': {
                'sequencial': resultado_apache_seq,
                'concorrente': resultado_apache_conc
            }
        }, f, indent=2)
    
    print(f"\n✓ Resultados salvos em: /app/resultados/teste_webservers_{timestamp}.json")
