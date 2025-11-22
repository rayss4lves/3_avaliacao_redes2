import subprocess
import src.cliente.gerar_arquivos

def menu():
    print("\n=== MENU ===")
    print("1) Iniciar containers")
    print("2) Executar testes")
    print("3) Parar containers")
    print("4) Ver logs")
    print("0) Sair")
    return input("\nEscolha: ")

def iniciar():
    print("\nIniciando containers...")
    subprocess.run(['docker-compose', 'up', '-d', '--build'])
    print("\n Containers iniciados!")
    print("  - Nginx:      http://95.58.0.2:8080")
    print("  - Apache:     http://95.58.0.4:8082")
    print("  - Prometheus: http://localhost:9090")
    print("  - Grafana:    http://localhost:3000")

def executar_testes():
    print("\nExecutando testes...")
    subprocess.run(['docker-compose', 'exec', 'client', 'python', '/app/src/cliente/testes.py'])
    print("\nTestes concluídos!")

def parar():
    print("\nParando containers...")
    subprocess.run(['docker-compose', 'down'])
    print("Containers parados!")

def logs():
    print("\nMostrando logs...")
    subprocess.run(['docker-compose', 'logs', '--tail=50'])


if __name__ == '__main__':
    
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
            print("Opção invalida!")