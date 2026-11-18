QUERY_BATERIA_MEDIA = """
    SELECT no_origem, DATE(instante) as dia, AVG(valor) as media_bateria
    FROM brenda_serie_limpa
    WHERE metrica = 'bateria'
    GROUP BY no_origem, DATE(instante);
"""

QUERY_UTILIZACAO_CANAL = """
    SELECT no_origem, HOUR(instante) as hora, AVG(valor) as media_canal
    FROM brenda_serie_limpa
    WHERE metrica = 'canal'
    GROUP BY no_origem, HOUR(instante);
"""
