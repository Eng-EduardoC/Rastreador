import socket
import json
from math import radians, sin, cos, sqrt, atan2

HOST = "0.0.0.0"
PORT = 8090

print("🚀 Servidor TCP iniciado!")
print(f"📡 Aguardando conexões na porta {PORT}...\n")


# ============================================================
# Conversão de coordenadas GT06
# ============================================================
def convert_coord(coord, direction):
    """
    Converte coordenadas GT06 para decimal.
    Latitude: DDMM.MMMM
    Longitude: DDDMM.MMMM
    """

    if not coord or coord == "0":
        return 0.0

    # LATITUDE (coord no formato DDMM.MMMM -> 4 dígitos antes do ponto)
    if len(coord.split('.')[0]) == 4:
        degrees = int(coord[:2])
        minutes = float(coord[2:])
    else:
        # LONGITUDE (coord no formato DDDMM.MMMM -> 5 dígitos antes do ponto)
        degrees = int(coord[:3])
        minutes = float(coord[3:])

    decimal = degrees + minutes / 60.0

    # Hemisfério Sul / Oeste -> negativo
    if direction in ["S", "W"]:
        decimal = -decimal

    return decimal


# ============================================================
# Cálculo de distância entre duas coordenadas
# ============================================================
def distancia_metros(lat1, lon1, lat2, lon2):
    R = 6371000  # raio da Terra em metros
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# ============================================================
# Carregar pontos do JSON
# ============================================================
def carregar_pontos():
    try:
        with open("pontos.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao ler pontos.json: {e}")
        return []

PONTOS = carregar_pontos()


# ============================================================
# Verificar se rastreador passou por um ponto
# ============================================================
def verificar_pontos(lat, lon):
    for ponto in PONTOS:
        nome = ponto["nome"]
        plat = ponto["lat"]
        plon = ponto["lon"]
        raio = ponto["raio_metros"]

        dist = distancia_metros(lat, lon, plat, plon)

        if dist <= raio:
            print(f"\n🚩 O rastreador PASSOU pelo ponto: **{nome}** (distância: {dist:.1f} m)\n")


# ============================================================
# Formatação do pacote GT06
# ============================================================
def format_packet(raw):
    try:
        data = raw.strip("#").split(",")

        imei = data[1]
        hora = data[3]
        status_gps = data[4]
        lat_raw = data[5]
        lat_dir = data[6]
        lon_raw = data[7]
        lon_dir = data[8]
        velocidade = data[9]
        direcao = data[10]
        data_raw = data[11]

        # Converter coordenadas
        lat = convert_coord(lat_raw, lat_dir)
        lon = convert_coord(lon_raw, lon_dir)

        # Formatando data/hora
        hora_fmt = f"{hora[0:2]}:{hora[2:4]}:{hora[4:6]}"
        dia = data_raw[0:2]
        mes = data_raw[2:4]
        ano = "20" + data_raw[4:6]
        data_fmt = f"{dia}/{mes}/{ano}"

        # Log bonito
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

        # Chama verificação dos pontos geográficos
        verificar_pontos(lat, lon)

        return log

    except Exception as e:
        return f"\n[ERRO AO FORMATAR PACOTE] {e}\nRAW={raw}\n"



# ============================================================
# Servidor TCP GT06
# ============================================================
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

        packet_log = format_packet(msg)
        print(packet_log)

    conn.close()
    print("🔌 Cliente desconectado.\n")

    #tetsete
    
