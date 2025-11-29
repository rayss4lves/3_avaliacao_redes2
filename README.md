# Terceira Avaliação de Redes de Computadores II - 2025-2

**UFPI - CSHNB | Sistemas de Informação | Trabalho Individual**

- **Autor**: Rayssa dos Santos Alves
- **Matrícula**: 20239019558
- **Entrega**: 28/11/2025
- [Link para o vídeo do YouTube](https://youtu.be/xNRojXApG2g))

## Avaliação Comparativa de Servidores Web com Docker, Prometheus e Grafana

Este projeto tem como objetivo configurar, testar e comparar o desempenho de dois servidores web — Nginx e Apache HTTP Server — utilizando uma stack de observabilidade baseada em Prometheus e Grafana, além de um cliente de carga implementado em Python.

## 🏗️ Estrutura

```
.
├── graficos/                          # Gráficos gerados das análises
│   ├── cpu.png
│   ├── latencia_media.png
│   └── memoria.png
|   └── rps.png
|   └── tempo_total.png
├── src/
│   ├── apache/                        # Servidor Apache HTTP
│   │   ├── html/                      # Arquivos HTML e TXT para os testes
│   │   ├── dockerfile.apache          # Dockerfile do Apache
│   │   └── httpd.conf                 # Configurações do Apache
│   ├── cliente/                       # Implementação do cliente de testes
│   │   ├── resultados/                # Resultados dos testes
│   │   ├── cliente.py                 
│   │   ├── gerar_arquivos.py          
│   │   ├── gerar_csvs.py              
│   │   ├── gerar_graficos.py          
│   │   ├── testes.py                  # Scripts de teste 
│   │   └── dockerfile.cliente         # Dockerfile do cliente
│   ├── grafana/                       # Configuração do Grafana
│   │   ├── dashboards/                # Dashboards personalizados
│   │   └── provisioning/              # Provisionamento automático
│   ├── nginx/                         # Servidor Nginx
│   │   ├── html/                      # Arquivos HTML e TXT para os testes
│   │   ├── dockerfile.nginx           # Dockerfile do Nginx
│   │   └── nginx.conf                 # Configurações do Nginx
│   ├── prometheus/                    # Configuração do Prometheus
│   │   └── prometheus.yml
├── run.py                             # Arquivo de execução do trabalho          
├── docker-compose.yaml                # Orquestração dos containers 
└── Avaliacao Redes 2 2025-2.pdf       # Especificação do trabalho

```

## 🔧 Tecnologias

- **Python 3.12** — Linguagem utilizada para implementação do cliente e scripts auxiliares.  
- **Docker** — Virtualização e isolamento dos containers que compõem o ambiente.  
- **Nginx** — Servidor Web utilizado para testes de desempenho.  
- **Apache** — Servidor Web utilizado para comparação com o Nginx.  
- **nginx-exporter** — Responsável por exportar métricas específicas do Nginx.  
- **apache-exporter** — Responsável por exportar métricas específicas do Apache.  
- **node-exporter** — Exporta métricas de uso dos containers (CPU, memória, etc.).  
- **Prometheus** — Captura e armazena métricas dos servidores e containers.  
- **Grafana** — Visualização dos dashboards e análise das métricas coletadas.  



## 🌐 Configuração de Rede

- **IPs baseados na matrícula**: Últimos 4 dígitos da matricula
- Subrede: `95.58.0.0/24`
  
| Serviço          | Hostname        | IP        | Porta     |
| ---------------- | --------------- | --------- | --------- |
| Nginx            | nginx           | 95.58.0.2 | 8080 → 80 |
| Nginx Exporter   | nginx-exporter  | 95.58.0.3 | 9113      |
| Apache           | apache-server   | 95.58.0.4 | 8081 → 80 |
| Apache Exporter  | apache-exporter | 95.58.0.5 | 9117      |
| Prometheus       | prometheus      | 95.58.0.6 | 9090      |
| Grafana          | grafana         | 95.58.0.7 | 3000      |
| Cliente (Tester) | cliente         | 95.58.0.8 | —         |

## 🚀 Como Executar

### Pré-requisitos
- Docker e Docker Compose instalados
- python instalado

### Execução
## 🚀 Como Executar o Projeto

### 1. Clonar repositório
```bash
git clone https://github.com/rayss4lves/3_avaliacao_redes2.git

cd 3_avaliacao_redes2

python run.py

```

## ## 🧪 Testes de Carga

Foram executados **9 cenários**, combinando diferentes tamanhos de arquivos e níveis de concorrência.  
Cada cenário foi repetido **20 vezes**, com **200 requisições por execução**, e as métricas foram coletadas automaticamente via **Prometheus**.

| Tamanho do Arquivo | Concorrência (Threads) | Execuções | Requisições por Execução | Coleta de Métricas |
|---------------------|------------------------|-----------|--------------------------|--------------------|
| 10 KB              | 5, 10, 15             | 20        | 200                      | Prometheus         |
| 1 MB               | 5, 10, 15             | 20        | 200                      | Prometheus         |
| 10 MB              | 5, 10, 15             | 20        | 200                      | Prometheus         |

## 📊 Métricas Avaliadas

- **Requisições por Segundo (RPS)**
- **Latência média, mínima e máxima**
- **Uso de CPU (%)**
- **Uso de memória (%)**
- **Taxa de sucesso/falhas**


**Professor**: Rayner Gomes 

---
