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
              totale = %s, \
              tempo = %s, \
              costo = %s, \
              roi = %s, \
              data = %s, \
              monke = %s \
              WHERE id = 1"
    else:
        sql = "INSERT INTO wallet (id, quantita, totale, tempo, costo, roi, data, monke) VALUES \
              (1, %s, %s, %s, %s, %s, %s, %s);"

    cur = conn.cursor()
    cur.execute(sql, (data["quantita"], data["totale"], data["tempo"], data["costo"],
                      data["roi"], data["data"], data["monke"]))
    conn.commit()
    cur.close()


def read():
    sql = "SELECT quantita, totale, tempo, costo, roi, data, monke FROM wallet WHERE id = 1"

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    cur.close()

    return result



#testing stuff
data = {
    "quantita": "5.234.765.432,34",
    "totale": "234632€",
    "tempo": "15min",
    "costo": "12,34€",
    "roi": "2999€",
    "data": "2021-03-01 18:42:21.62228",
    "monke": "false"
}
write(data)
print(read())
