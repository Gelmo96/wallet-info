import database
import datetime
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    db_data = database.read()[0]
    print("Dati ricevuti dal db:",db_data)
    time_old = datetime.datetime.strptime(db_data["data"], '%Y-%m-%d %H:%M:%S.%f')
    time_now = datetime.datetime.now()
    diff = time_now - time_old
    seconds_in_day = 24 * 60 * 60
    time_res = divmod(diff.days * seconds_in_day + diff.seconds, 60)
    minuti = "{}min {}s".format(abs(time_res[0]), time_res[1])
    print("minuti differenza:", minuti)
    web_data = {
        "data": {
            "Quantita": db_data["quantita"],
            "Totale wallet": db_data["totale"],
            "Tempo esecuzione": db_data["tempo"],
            "Costo gas": db_data["costo"],
            "ROI individuale": db_data["roi"]
        },
        "page_info": {
            "min": minuti,
            "monke": db_data["monke"]
        }
    }
    return render_template('index.html', data=web_data)

if __name__ == "__main__":
    app.run()