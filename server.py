import socket

HOST = "0.0.0.0"   # escuta em todas interfaces
PORT = 5015        # porta que o rastreador vai enviar

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Servidor ouvindo na porta {PORT}...")

while True:
    conn, addr = server.accept()
    print("Conexão de:", addr)

    while True:
        data = conn.recv(1024)
        if not data:
            break
        try:
            print("Dados recebidos:", data.decode(errors="ignore"))
        except:
            print("Erro ao decodificar pacote")
    
    conn.close()
