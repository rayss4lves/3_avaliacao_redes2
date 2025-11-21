import socket
import hashlib
import time

# Gera um hash SHA1 fixo usado como X-Custom-ID para as requisicoes
def gerar_hash():
        chave = '20239019558 Rayssa Alves'
        sha1_hash = hashlib.sha1(chave.encode()).hexdigest()
        print(sha1_hash)
        return sha1_hash

X_CUSTOM_ID = gerar_hash()
 
class Cliente():
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta
        
    def dividir_requisicao(self, requisicao):
        cabecalhos = {}
        metodo_requisicao = None
        caminho_requisicao = None
        try:
            linhas_requisicao = requisicao.decode('utf-8', errors='ignore').split('\r\n')
            if linhas_requisicao or linhas_requisicao[0]:
                campos_requisicao = linhas_requisicao[0].split()

                if len(campos_requisicao) >= 3:
                    metodo_requisicao, caminho_requisicao, _ = campos_requisicao[0], campos_requisicao[1], campos_requisicao[2] 
                
                for linha in linhas_requisicao[1:]:
                    if ':' in linha:
                        chave, valor = linha.split(':', 1)
                        cabecalhos[chave.strip()] = valor.strip()
            
            
        except Exception as e:
            print(f"Erro ao analisar a requisicao: {e}")
        
        return metodo_requisicao, caminho_requisicao, cabecalhos
    
    # Esta funcao monta e envia uma requisicao HTTP via socket TCP e retorna (success, tempo, resposta)
    # Ela usa o X-Custom-ID no cabecalho da requisicao
    def enviar_requisicao(self, metodo='GET', caminho = '/', corpo=None):
        tempo_inicial = time.time()
        
        try:
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect((self.host, self.porta))
            
            # Monta a requisicao HTTP
            cabecalhos = [f"Host: {self.host}", f"X-Custom-ID: {X_CUSTOM_ID}"]
            
            corpo_texto = ""
            if corpo:
                corpo_texto = str(corpo)
                cabecalhos.append(f"Content-Length: {len(corpo_texto.encode('utf-8'))}")

            cabecalhos_str = "\r\n".join(cabecalhos)
            request = f"{metodo} {caminho} HTTP/1.1\r\n{cabecalhos_str}\r\n\r\n{corpo_texto}"
                
            #3 Enviando a requisicao
            
            client_socket.sendall(request.encode())
            
            #recebendo a resposta
            
            resposta = client_socket.recv(8192)
            tempo_total = time.time() - tempo_inicial
            
            client_socket.close()
            
            metodo_requisicao, caminho_requisicao, cabecalhos_recebidos = self.dividir_requisicao(resposta)
            
            resposta_status = resposta.decode(errors='ignore')
            cod_status = 0
            
            if resposta_status.startswith('HTTP/1.1'):
                try:
                    cod_status = int(resposta_status.split(' ')[1])
                except:
                    cod_status = 0
            
            custom_id_recebido = cabecalhos_recebidos.get('X-Custom-ID', None)
            custom_id_esperado = X_CUSTOM_ID
            
            return {
                    'codigo_status': cod_status,
                    'tempo_total': tempo_total,
                    'cabecalhos': cabecalhos_recebidos,
                    'sucesso':cod_status >= 200 and cod_status < 300,
                    'X-Custom-ID': custom_id_recebido,
                    'X-Custom-ID-Esperado': custom_id_esperado
            }
        except Exception as e:
            print(f'Error: {e}')
            return {
                'codigo_status': 0,
                'tempo_total': tempo_total,
                'cabecalhos': {},
                'sucesso':False,
                'erro': str(e)
            }
        

