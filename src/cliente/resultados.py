import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
 
import csv
import os
from datetime import datetime


# Esta funcao salva os resultados de cada exeecucao em um CSV, na pasta de resultados
def salvar_execucoes_csv(resultados, nome_servidor, arquivo='resultados/execucoes.csv'):
    #Diretorio base e criacao da pasta resultados para salvar o arquivo CSV
    os.makedirs(os.path.dirname(arquivo) if os.path.dirname(arquivo) else '.', exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    linhas = []
    for cenario, execucoes in resultados.items():
        for i, execucao in enumerate(execucoes, start=1):
            linha = {
                "timestamp": timestamp,
                "servidor": nome_servidor,
                "cenario": cenario,
                "execucao": i,
            }
            # Adiciona todas as metricas do dicionario de Resposta na linha
            linha.update(execucao)
            linhas.append(linha)
    
    if linhas:
        campos = ['timestamp', 'servidor', 'cenario', 'execucao', 'Falhas', 'Tempo_Total', 'Throughput', 'Requisicões Bem Sucedidas', 'Tempo_Medio_Resposta'] 

        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(linhas)
 
    
# Esta funcao salva as estatisticas calculadas no CSV, na pasta resultados
def salvar_estatisticas_csv(estatisticas, nome_servidor, arquivo='resultados/estatisticas.csv'):
   
    #Diretorio base e criacao da pasta resultados para salvar o arquivo CSV
    os.makedirs(os.path.dirname(arquivo) if os.path.dirname(arquivo) else '.', exist_ok=True)

    linhas = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for cenario, metricas in estatisticas.items():
        for metrica_nome, valores in metricas.items():
            linha = {
                "timestamp": timestamp,
                "servidor": nome_servidor,
                "cenario": cenario,
                "metrica": metrica_nome,
                "media": valores['Media'],
                "desvio_padrao": valores['Desvio Padrao']
            }
            linhas.append(linha)

    if linhas:
        campos = ['timestamp', 'servidor', 'cenario', 'metrica', 'media', 'desvio_padrao']
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(linhas)
  

# Esta funcao utiliza a biblioteca NumPy para calcular a media e desvio padrao para cada metrica
def calcular_estatisticas(resultados):
    
    resultados_estatisticas = {}
    
    for cenario, execucoes in resultados.items():
        resultados_estatisticas[cenario] = {}
        
        campos = execucoes[0].keys()
        
        for campo in campos:
            valores = []
            
            for execucao in execucoes:
                valores.append(execucao[campo])
            media = np.mean(valores)
            desvio = np.std(valores, ddof=1) if len(valores) > 1 else 0.0
            resultados_estatisticas[cenario][campo] = {'Media': media, 'Desvio Padrao': desvio}
        
    return resultados_estatisticas

# Esta funcao mostra resultados estatisticos formatados no terminal
def mostrar_resultados(estatisticas):
    
    print('================================= RESULTADOS DAS ESTATiSTICAS =================================')
    
    for cenario, metricas in estatisticas.items():
        for metrica, valores in metricas.items():
            media = valores['Media']
            desvio = valores['Desvio Padrao']
            print(f"  {metrica:.<40} Média: {media:>10.2f} | Desvio: {desvio:>10.2f}")

# Esta funcao gera um grafico de linha comparando vazao entre servidores ao longo das execucoes
def grafico_vazao_execucoes(arquivo_sincrono='resultados_sincrono.csv', arquivo_assincrono='resultados_assincrono.csv', output='../../graficos/vazao_execucoes.png'):
    
    # Diretorio base e criacao da pasta graficos
    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else '.', exist_ok=True)

    # Carregar dados
    df_sincrono = pd.read_csv(arquivo_sincrono)
    df_assincrono = pd.read_csv(arquivo_assincrono)

    # Obtendo a lista da coluna Throughput
    vazao_sincrono = df_sincrono['Throughput'].tolist()
    vazao_assincrono = df_assincrono['Throughput'].tolist()

    # Criar figura
    plt.figure(figsize=(14, 8))
    plt.plot(range(1, len(vazao_sincrono) + 1), vazao_sincrono, marker='o', label='Servidor Sequencial')
    plt.plot(range(1, len(vazao_assincrono) + 1), vazao_assincrono, marker='s', label='Servidor Concorrente')

    plt.xlabel('Número da Resposta')
    plt.ylabel('Vazao')
    plt.title('Comparaçao de Vazao: Sequencial vs Concorrente')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()

# Esta funcao gera um grafico de linha comparando tempos de resposta ao longo das execucoes   
def grafico_tempo_execucoes(arquivo_sincrono='resultados_sincrono.csv', arquivo_assincrono='resultados_assincrono.csv', output='../../graficos/tempo_execucoes.png'):
    # Diretorio base e criaçao da pasta graficos
    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else '.', exist_ok=True)

    # Carregar dados
    df_sincrono = pd.read_csv(arquivo_sincrono)
    df_assincrono = pd.read_csv(arquivo_assincrono)

    # Obter lista da coluna de tempo
    tempo_sincrono = df_sincrono['Tempo_Medio_Resposta'].tolist()
    tempo_assincrono = df_assincrono['Tempo_Medio_Resposta'].tolist()

    # Criar figura
    plt.figure(figsize=(14, 8))
    plt.plot(range(1, len(tempo_sincrono) + 1), tempo_sincrono, marker='o', label='Servidor Sequencial')
    plt.plot(range(1, len(tempo_assincrono) + 1), tempo_assincrono, marker='s', label='Servidor Concorrente')

    plt.xlabel('Número da Resposta')
    plt.ylabel('Tempo de Resposta (s)')
    plt.title(f'Comparaçao de Tempo médio de Resposta: Sequencial vs Concorrente')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()

    
# Esta funcao gera um grafico de barras comparando throughput medio entre os servidores   
def grafico_barras_throughput(arquivo_sincrono='resultados_sincrono.csv', arquivo_assincrono='resultados_assincrono.csv', output='../../graficos/barras_throughput.png'):

    # Diretorio base e criacao da pasta graficos
    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else '.', exist_ok=True)

    # Carregando os dados
    df_sincrono = pd.read_csv(arquivo_sincrono)
    df_assincrono = pd.read_csv(arquivo_assincrono)

    # Filtrando apenas a metrica Throughput
    tp_sincrono = df_sincrono.loc[df_sincrono['metrica'] == 'Throughput', 'media'].values[0]
    tp_assincrono = df_assincrono.loc[df_assincrono['metrica'] == 'Throughput', 'media'].values[0]
    
    # Obtendo o desvio padrao
    std_sincrono = df_sincrono.loc[df_sincrono['metrica'] == 'Throughput', 'desvio_padrao'].values[0]
    std_assincrono = df_assincrono.loc[df_assincrono['metrica'] == 'Throughput', 'desvio_padrao'].values[0]

    # Criando o grafico de barras
    servidores = ['Sequencial', 'Concorrente']
    valores = [tp_sincrono, tp_assincrono]
    desvios = [std_sincrono, std_assincrono]

    plt.figure(figsize=(8, 6))
    barras = plt.bar(servidores, valores, color=['skyblue', 'salmon'])
    
    plt.errorbar(servidores, valores, yerr=desvios, fmt='none', ecolor='black', 
                 capsize=8, capthick=2, elinewidth=2)
    
    plt.ylabel('Throughput')
    plt.title('Comparação de Média de Throughput')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # For para adicionar valores medios no topo das barras
    for i, barra in enumerate(barras):
        altura = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2, altura + desvios[i] + altura*0.01, 
                 f"{altura:.2f}", ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
