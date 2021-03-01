from flask import Flask, render_template
from wallet_info import get_data

app = Flask(__name__)

@app.route("/")
def main():
    res = get_data()
    return render_template('index.html', data=res)

if __name__ == "__main__":
    app.run()