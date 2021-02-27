from flask import Flask
from flask import Flask, render_template
from wallet_info import feg

app = Flask(__name__)

@app.route("/")
def main():
    res = feg()
    #res = {}
    return render_template('index.html', data=res)

if __name__ == "__main__":
    app.run()