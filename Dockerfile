FROM python:3.10-slim

WORKDIR /app

# Copia os ficheiros de dependências e instala-os
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código do projeto
COPY . .