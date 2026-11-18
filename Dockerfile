FROM python:3.10-slim

WORKDIR /app

# Copia os ficheiros do projeto
COPY requirements.txt .
COPY . .

# Copia diretamente os pacotes do Python local (site-packages) do teu Linux para dentro do Docker!
COPY /home/usuario/.local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages