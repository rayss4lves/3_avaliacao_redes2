#!/usr/bin/env python3
"""Script simples para gerenciar o projeto"""

import subprocess
import sys
from src.cliente.gerar_arquivos import gerar_arquivo

def menu():
    print("\n=== MENU ===")
    print("1) Iniciar containers")
    print("2) Executar testes")
    print("3) Parar containers")
    print("4) Ver logs")
    print("0) Sair")
    return input("\nEscolha: ")

def iniciar():
    print("\n[+] Iniciando containers...")
    subprocess.run(['docker-compose', 'up', '-d', '--build'])
    print("\n✓ Containers iniciados!")
    print("  - Nginx:      http://localhost:8080")
    print("  - Apache:     http://localhost:8082")
    print("  - Prometheus: http://localhost:9090")
    print("  - Grafana:    http://localhost:3000")

def executar_testes():
    print("\n[+] Executando testes...")
    subprocess.run(['docker-compose', 'exec', 'client', 'python', '/app/src/cliente/testes.py'])
    print("\n✓ Testes concluídos!")

def parar():
    print("\n[+] Parando containers...")
    subprocess.run(['docker-compose', 'down'])
    print("✓ Containers parados!")

def logs():
    print("\n[+] Mostrando logs...")
    subprocess.run(['docker-compose', 'logs', '--tail=50'])


if __name__ == '__main__':
    # Se passar argumento direto
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        if comando == 'iniciar':
            iniciar()
        elif comando == 'testes':
            executar_testes()
        elif comando == 'parar':
            parar()
        elif comando == 'logs':
            logs()
        else:
            print("Comandos: iniciar, testes, parar, logs")
        sys.exit(0)
    
    # Menu interativo
    while True:
        escolha = menu()
        
        if escolha == '1':
            iniciar()
        elif escolha == '2':
            executar_testes()
        elif escolha == '3':
            parar()
        elif escolha == '4':
            logs()
        elif escolha == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")