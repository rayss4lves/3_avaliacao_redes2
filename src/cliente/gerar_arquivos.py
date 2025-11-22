import os

def gerar_arquivo(caminho, nome, tamanho_kb):
    os.makedirs(caminho, exist_ok=True)
    with open(os.path.join(caminho, nome), 'w') as f:
        f.write('A' * 1024 * tamanho_kb)

# Caminhos para NGINX e Apache
# Diretório base do projeto (onde o script está salvo)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Caminhos corretos para NGINX e Apache dentro da pasta src já existente
caminho_nginx = os.path.join(base_dir, "..", "nginx", "html")
caminho_apache = os.path.join(base_dir, "..", "apache", "html")

# Arquivos de teste
gerar_arquivo(caminho_nginx, "arquivo_10kb.txt", 10)
gerar_arquivo(caminho_nginx, "arquivo_1mb.txt", 1024)
gerar_arquivo(caminho_nginx, "arquivo_10mb.txt", 10 * 1024)

gerar_arquivo(caminho_apache, "arquivo_10kb.txt", 10)
gerar_arquivo(caminho_apache, "arquivo_1mb.txt", 1024)
gerar_arquivo(caminho_apache, "arquivo_10mb.txt", 10 * 1024)

print("Arquivos gerados em src/nginx/html e src/apache/html")
