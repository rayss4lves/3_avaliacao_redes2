import socket
import hashlib
import time
import threading
from testes import teste_sequencial, teste_concorrente
from resultados import calcular_estatisticas, mostrar_resultados, salvar_execucoes_csv
from resultados import salvar_estatisticas_csv, grafico_vazao_execucoes, grafico_barras_throughput, grafico_tempo_execucoes

# Gera um hash SHA1 fixo usado como X-Custom-ID para as requisicoes
def gerar_hash():
        chave = '20239019558 Rayssa Alves'
        sha1_hash = hashlib.sha1(chave.encode()).hexdigest()
        print(sha1_hash)
        return sha1_hash

X_CUSTOM_ID = gerar_hash()
MAX_THREADS = 10
NUM_REQUISICOES_SEQ = 50
NUM_REQ_CONCORRENTE = 50
NUM_EXECUCOES = 20
 
class Cliente():
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta
    
    # Esta funcao monta e envia uma requisicao HTTP via socket TCP e retorna (success, tempo, resposta)
    # Ela usa o X-Custom-ID no cabecalho da requisicao
    def enviar_requisicao(self, metodo='GET', caminho = '/', corpo=None):
        
        try:
            tempo_inicial = time.time()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect((self.host, self.porta))
            
            # Monta a requisicao HTTP
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
            success = b"200 OK" in resposta
            
            return success, response_time, resposta.decode()
        except Exception as e:
            print(f"Error: {e}")
            return False, 0, str(e)
        

if __name__ == "__main__":

    servidor_host_sincrono = 'servidor-sincrono'
    servidor_porta_sincrono = 80
    
    servidor_host_assincrono = 'servidor-assincrono' 
    servidor_porta_assincrono = 80
    
    resultados_sincrono = {}
    resultados_assincrono = {}
    
    
    print('=======================TESTE DO SERVIDOR SINCRONO=======================')
    
    print('-----------Teste inicial-----------')
    cliente = Cliente(servidor_host_sincrono, servidor_porta_sincrono)
    success, response_time, resposta = cliente.enviar_requisicao(metodo='GET', caminho='/')
    print(f"\nSuccess: {success}, Response Time: {response_time}")
    print(resposta)
    
    resultados_sincrono['GET - /'] = []
    for i in range(NUM_EXECUCOES):
        print(f'------------------ Execucao {i+1} ------------------')
        resultado_sincrono = teste_sequencial(metodo='GET', caminho='/', num_requisicoes=NUM_REQUISICOES_SEQ, cliente=cliente)
        resultados_sincrono['GET - /'].append(resultado_sincrono)
     
        
    print('======================TESTE DO SERVIDOR ASSINCRONO======================')
    
    print('-----------Teste inicial-----------')
    cliente = Cliente(servidor_host_assincrono, servidor_porta_assincrono)
    success, response_time, resposta = cliente.enviar_requisicao(metodo='GET', caminho='/')
    print(f"\nSuccess: {success}, Response Time: {response_time}")
    print(resposta)
    resultados_assincrono['GET - /'] = []
    for i in range(NUM_EXECUCOES):
        print(f'------------------ Execucao {i+1} ------------------')
        resultado_assincrono = teste_concorrente(metodo='GET', caminho='/', num_requisicoes = NUM_REQ_CONCORRENTE,  num_threads = MAX_THREADS, cliente=cliente)
        resultados_assincrono['GET - /'].append(resultado_assincrono)
            
    
    print('======================ESTATISTICAS DO SERVIDOR SINCRONO======================')
    # Calcular estatisticas
    stats_sinc = calcular_estatisticas(resultados_sincrono)
    
    # Mostrar resultados
    mostrar_resultados(stats_sinc)
    
    print('======================ESTATISTICAS DO SERVIDOR ASSINCRONO======================')
    # Calcular estatisticas
    stats_assinc = calcular_estatisticas(resultados_assincrono)
    
    mostrar_resultados(stats_assinc)

    #SALVANDO OS CSVs
    salvar_execucoes_csv(resultados_sincrono, 'sequencial', arquivo='resultados/sincrono.csv')
    salvar_execucoes_csv(resultados_assincrono, 'concorrente', arquivo='resultados/assincrono.csv')
 
    salvar_estatisticas_csv(stats_sinc, nome_servidor='sincrono', arquivo='resultados/resultados_sincrono.csv')
    salvar_estatisticas_csv(stats_assinc, nome_servidor='assincrono', arquivo='resultados/resultados_assincrono.csv')
    
    
    #EXECUTANDO OS GRAFICOS

    grafico_vazao_execucoes('resultados/sincrono.csv', 'resultados/assincrono.csv', '../../graficos/vazao_execucoes.png')
    grafico_barras_throughput('resultados/resultados_sincrono.csv', 'resultados/resultados_assincrono.csv', '../../graficos/barras_throughput.png')
    grafico_tempo_execucoes('resultados/sincrono.csv', 'resultados/assincrono.csv', '../../graficos/tempo_execucoes.png')

 