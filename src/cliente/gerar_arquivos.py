import os

def gerar_arquivo(caminho, nome, tamanho_kb):
    os.makedirs(caminho, exist_ok=True)
    with open(os.path.join(caminho, nome), 'w') as f:
        f.write('A' * 1024 * tamanho_kb)

# Caminhos para NGINX e Apache
caminho_nginx = "src/nginx/html"
caminho_apache = "src/apache/html"

# Arquivos de teste
gerar_arquivo(caminho_nginx, "arquivo_5kb.txt", 5)
gerar_arquivo(caminho_nginx, "arquivo_5mb.txt", 5 * 1024)

gerar_arquivo(caminho_apache, "arquivo_5kb.txt", 5)
gerar_arquivo(caminho_apache, "arquivo_5mb.txt", 5 * 1024)

print("Arquivos gerados em src/nginx/html e src/apache/html")
