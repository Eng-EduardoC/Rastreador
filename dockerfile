FROM python:3.10-slim

# Instalar dependências opcionais (caso seu projeto cresça)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Porta alta (evita problemas de bind no Windows)
ENV SERVER_PORT=8090

WORKDIR /app

# Copia todo o código
COPY . /app

# Expor a porta para debug/ligações
EXPOSE 8090

# Mostrar logs sem buffer (muito importante!)
ENV PYTHONUNBUFFERED=1

# Rodar o servidor
CMD ["python", "server.py"]
