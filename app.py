from flask import Flask
import index
import wallet_cero

app = Flask(__name__)

@app.route("/")
@app.route("/home")
@app.route("/index")
def _index():
    return index.load()

@app.route("/wallet_cero")
def _wallet_cero():
    return wallet_cero.load()

if __name__ == "__main__":
    app.run()