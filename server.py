import socket

HOST = "0.0.0.0"
PORT = 8090

print("Iniciando servidor TCP...")
print(f"Escutando na porta {PORT}...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

while True:
    conn, addr = server.accept()
    print("Conexão de:", addr)

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print("Dados recebidos:", data.decode(errors="ignore"))

    conn.close()
