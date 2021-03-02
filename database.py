import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def write(data):
    cur = conn.cursor()
    cur.execute("SELECT * FROM wallet WHERE id = 1")

    # se la linea è presente in tabella
    if cur.fetchone() is not None:
        sql = "UPDATE wallet \
                SET quantita = %s, \
                totale_eur = %s, \
                totale_usd = %s, \
                tempo = %s, \
                gas_eur = %s, \
                gas_usd = %s, \
                data = %s \
                WHERE id = 1"
    else:
        sql = "INSERT INTO wallet (id, quantita, totale_eur, totale_usd, tempo, gas_eur, gas_usd, data) VALUES \
              (1, %s, %s, %s, %s, %s, %s, %s);"

    cur = conn.cursor()
    cur.execute(sql, (data["quantita"], data["totale_eur"], data["totale_usd"], data["tempo"], data["gas_eur"],
                      data["gas_usd"], data["data"]))
    conn.commit()
    cur.close()


def read():
    sql = "SELECT quantita, totale_eur, totale_usd, tempo, gas_eur, gas_usd, data FROM wallet WHERE id = 1"

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    cur.close()

    return result

'''
#testing stuff
data = {
    "quantita": "5.234.765.432,34",
    "totale_eur": "234632€",
    "totale_usd": "234632$",
    "tempo": "15min",
    "gas_eur": "12,34€",
    "gas_usd": "12,34€",
    "data": "2021-03-01 18:42:21.62228",
    }
write(data)
print(read())
'''