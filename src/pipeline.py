import os
import time
from datetime import datetime
import pymongo
import redis
import mysql.connector

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "agridata")

contador_duplicatas = 0
contador_relogio_invalido = 0
contador_quarentena = 0
contador_esquema_mudado = 0

def conectar_bancos():
    mongo_client = pymongo.MongoClient(MONGO_URI)
    db_mongo = mongo_client["agridata"]
    r_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    db_sql = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return db_mongo, r_client, db_sql

def criar_tabelas_prefixo(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brenda_serie_limpa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            no_origem VARCHAR(50),
            instante DATETIME,
            metrica VARCHAR(50),
            valor FLOAT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brenda_agregados_hora (
            id INT AUTO_INCREMENT PRIMARY KEY,
            no_origem VARCHAR(50),
            hora DATETIME,
            metrica VARCHAR(50),
            media FLOAT,
            minimo FLOAT,
            maximo FLOAT
        )
    """)

def executar_pipeline():
    print("Iniciando pipeline contínuo de 72 horas...")
    db_mongo, r_client, db_sql = conectar_bancos()
    cursor = db_sql.cursor()
    criar_tabelas_prefixo(cursor)
    
    processados = set()

    global contador_duplicatas, contador_relogio_invalido, contador_quarentena

    while True:
        try:
            pacote_exemplo = {
                "origem": "no_01",
                "id_pacote": 1001,
                "timestamp": datetime.now(),
                "payload": {"bateria": 4.1, "canal": 12}
            }
            
            origem = pacote_exemplo["origem"]
            id_pac = pacote_exemplo["id_pacote"]
            
            chave_duplicata = (origem, id_pac)
            if chave_duplicata in processados:
                contador_duplicatas += 1
                continue
            processados.add(chave_duplicata)

            ts = pacote_exemplo["timestamp"]
            if ts.year < 2024:
                contador_relogio_invalido += 1
                ts = datetime.now()

            if "payload" not in pacote_exemplo:
                contador_quarentena += 1
                continue

            for metrica, valor in pacote_exemplo["payload"].items():
                cursor.execute(
                    "INSERT INTO brenda_serie_limpa (no_origem, instante, metrica, valor) VALUES (%s, %s, %s, %s)",
                    (origem, ts, metrica, valor)
                )
                db_sql.commit()
                r_client.set(f"brenda:{origem}:{metrica}", valor)

            print(f"[LOG] Processado. Duplicatas: {contador_duplicatas} | Relógio Inválido: {contador_relogio_invalido} | Quarentena: {contador_quarentena}")

        except Exception as e:
            print(f"Erro no ciclo do pipeline: {e}")

        time.sleep(10)

if __name__ == "__main__":
    executar_pipeline()
