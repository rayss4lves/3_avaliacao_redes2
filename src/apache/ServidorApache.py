import http.server
import socketserver
import datetime 
import json
import os
from urllib.parse import urlparse

PORT = 80

class ApacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Log do X-Custom-ID
        x_custom_id = self.headers.get('X-Custom-ID', 'N/A')
        print(f"[{datetime.now().isoformat()}] Apache: {self.command} {path} - X-Custom-ID: {x_custom_id}")
        
        # Endpoint de status da API
        if path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'status': 'ok',
                'server': 'python-apache',
                'timestamp': datetime.now().isoformat(),
                'x_custom_id': x_custom_id
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Server status para métricas
        if path == '/server-status':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            status = f"""Total Accesses: 1
Total kBytes: 1
CPULoad: 0.1
Uptime: 100
ReqPerSec: 0.01
BytesPerSec: 10.24
BytesPerReq: 1024
BusyWorkers: 1
IdleWorkers: 9
"""
            self.wfile.write(status.encode())
            return
        
        # Servir arquivos normalmente
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Log customizado
        pass

def main():
    # Mudar para o diretório com os arquivos HTML
    os.chdir('/app/html')
    
    with socketserver.TCPServer(("", PORT), ApacheHTTPRequestHandler) as httpd:
        print(f"========================================")
        print(f"Servidor Python (Apache) rodando na porta {PORT}")
        print(f"Aluno: Hermeson A.")
        print(f"Matrícula: 20239035382")
        print(f"========================================")
        httpd.serve_forever()

if __name__ == '__main__':
    main()