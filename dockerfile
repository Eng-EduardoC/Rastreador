FROM python:3.10-slim

WORKDIR /app

COPY server.py /app/server.py

CMD ["python", "server.py"]
