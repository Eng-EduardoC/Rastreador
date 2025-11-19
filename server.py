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

        # Campos do protocolo GT06
        lat_raw = data[5]
        lat_dir = data[6]
        lon_raw = data[7]
        lon_dir = data[8]

        # Converter coordenadas
        lat = convert_coord(lat_raw, lat_dir)
        lon = convert_coord(lon_raw, lon_dir)

        # ==== CÁLCULO DE DISTÂNCIA PARA CADA PONTO ====
        distancias_texto = "\nDistâncias aos pontos:\n"
        for ponto in PONTOS:
            nome = ponto["nome"]
            plat = ponto["lat"]
            plon = ponto["lon"]

            dist = distancia_metros(lat, lon, plat, plon)
            distancias_texto += f"- {nome}: {dist:.1f} metros\n"

        # ==== MENSAGEM QUANDO ENTRA NO RAIO ====
        for ponto in PONTOS:
            nome = ponto["nome"]
            plat = ponto["lat"]
            plon = ponto["lon"]
            raio = ponto["raio_metros"]

            dist = distancia_metros(lat, lon, plat, plon)

            if dist <= raio:
                print(f"\n🚩 PASSOU PELO PONTO: {nome} (distância: {dist:.1f} m)\n")

        # ==== LOG LIMPO ====
        log = (
            "\n====== 📍 LOCALIZAÇÃO RECEBIDA ======\n"
            f"Latitude:  {lat:.6f}\n"
            f"Longitude: {lon:.6f}\n\n"
            "🔗 Google Maps:\n"
            f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}\n"
            f"{distancias_texto}"
            "=====================================\n"
        )

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
    
