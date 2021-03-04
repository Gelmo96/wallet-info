import database
import datetime
from flask import render_template

def load():
    db_data = database.read()[0]
    print("wallet_cero.load: dati ricevuti dal db:\t", db_data)
    time_old = datetime.datetime.strptime(db_data["data"], '%Y-%m-%d %H:%M:%S.%f')

    investimento_iniziale = 116
    roi = ((float(db_data["totale_eur"]) - float(db_data["gas_eur"])) / 3) - investimento_iniziale

    monke = False
    # we did it boys
    if roi >= 0:
        roi = "+{0:.2f}€ \U0001F680\U0001F680\U0001F680".format(roi)
        monke = True
    else:
        roi = "{0:.2f}€".format(roi)

    web_data = {
        "data": {
            "Quantita": db_data["quantita"],
            "Totale wallet": db_data["totale_eur"] + "€",
            "Tempo esecuzione": db_data["tempo"] + "min",
            "Costo gas": db_data["gas_eur"] + "€",
            "ROI individuale": roi
        },
        "page_info": {
            "time": time_old,
            "monke": monke
        }
    }

    return render_template('wallet_cero.html', data=web_data)