import socket

HOST = "0.0.0.0"
PORT = 8090

print("🚀 Servidor TCP iniciado!")
print(f"📡 Aguardando conexões na porta {PORT}...\n")

def convert_coord(coord, direction):
    """
    Converte coordenadas GT06 para decimal.
    Latitude: DDMM.MMMM
    Longitude: DDDMM.MMMM
    """

    if not coord or coord == "0":
        return 0.0

    # LATITUDE (coord no formato DDMM.MMMM → primeiros 2 dígitos)
    if len(coord.split('.')[0]) == 4:  
        degrees = int(coord[:2])
        minutes = float(coord[2:])
    else:
        # LONGITUDE (coord no formato DDDMM.MMMM → primeiros 3 dígitos)
        degrees = int(coord[:3])
        minutes = float(coord[3:])

    decimal = degrees + minutes / 60

    # Inverte para hemisfério Sul ou Oeste
    if direction in ["S", "W"]:
        decimal = -decimal

    return decimal



def format_packet(raw):
    try:
        data = raw.strip("#").split(",")

        imei = data[1]
        protocolo = data[2]
        hora = data[3]                     # HHMMSS
        status_gps = data[4]
        lat_raw = data[5]
        lat_dir = data[6]
        lon_raw = data[7]
        lon_dir = data[8]
        velocidade = data[9]
        direcao = data[10]
        data_raw = data[11]                # DDMMYY

        # Conversão de coordenadas
        lat = convert_coord(lat_raw, lat_dir)
        lon = convert_coord(lon_raw, lon_dir)

        # Formatar hora
        hora_fmt = f"{hora[0:2]}:{hora[2:4]}:{hora[4:6]}"

        # Formatar data
        dia = data_raw[0:2]
        mes = data_raw[2:4]
        ano = "20" + data_raw[4:6]

        data_fmt = f"{dia}/{mes}/{ano}"

        # Monta o log bonitão
        log = (
            "\n====== 📡 PACOTE GT06 RECEBIDO ======\n"
            f"IMEI: {imei}\n"
            f"Data/Hora: {data_fmt} {hora_fmt}\n"
            f"Latitude: {lat:.6f}\n"
            f"Longitude: {lon:.6f}\n\n"
            "🔗 Google Maps:\n"
            f"{lat:.6f}, {lon:.6f}\n"
            f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}\n\n"
            "--------------------------------------\n"
            f"RAW: {raw}\n"
            "======================================\n"
        )

        return log

    except Exception as e:
        return f"\n[ERRO AO FORMATAR PACOTE] {e}\nRAW={raw}\n"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

while True:
    conn, addr = server.accept()
    print(f"🔌 Conexão de: {addr}")

    while True:
        data = conn.recv(2048)
        if not data:
            break

        msg = data.decode(errors="ignore")

        # Formatação do pacote
        packet_log = format_packet(msg)
        print(packet_log)

    conn.close()
    print("🔌 Cliente desconectado.\n")
