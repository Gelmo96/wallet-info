from flask import Flask
import index
import wallet_cero
import wallet_info

app = Flask(__name__)

@app.route("/")
@app.route("/home")
@app.route("/index")
def _index():
    return index.load_page()

@app.route("/wallet_cero")
def _wallet_cero():
    return wallet_cero.load_page()

@app.route("/collect_data")
def _collect_data():
    return wallet_info.get_data()

if __name__ == "__main__":
    app.run()