import os
import locale
import database
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from currency_converter import CurrencyConverter


def make_request(url):
    headers = requests.utils.default_headers()

    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'})

    return requests.get(url, headers=headers).json()

def eth_price():
    key = os.environ.get('DEFIPULSE_KEY')
    url = "https://data-api.defipulse.com/api/v1/dexag/markets?api-key=" + key

    # ritorno il prezzo in USDC per un ETH
    return make_request(url)["AG"]["ETH-USDC"]["ask"]

def gas_price():
    key = os.environ.get('DEFIPULSE_KEY')
    url = "https://data-api.defipulse.com/api/v1/egs/api/ethgasAPI.json?api-key=" + key

    res = make_request(url)
    # costo medio di una quantità di gas in wei
    gwei_cost = res["average"] / 10
    print("costo di 1 gas in wei:", gwei_cost)
    # costo in eth di un gas
    eth = gwei_cost * (1 * 10 ** -9)
    # costo di tutta la transazione in eth
    # 200.000 ammontare medio di gas per una transazione di FEG
    eth = float(eth * 200000)
    eth_price_usd = float(eth_price())
    print("eth_price", eth_price_usd)
    transaction_cost = eth * eth_price_usd
    print("total transaction cost", transaction_cost)
    # tempo in minuti per completare la transazione
    time_to_complete = res["avgWait"]
    print("tempo esecuzione:", str(time_to_complete) + "minuti")

    return {
        "time_to_complete" : time_to_complete,
        "transaction_cost" : transaction_cost
    }

def usd_to_eur(cash):
    c = CurrencyConverter()
    cash = c.convert(cash, 'USD', 'EUR')
    return cash

def feg():
    #https://etherscan.io/token/0x389999216860ab8e0175387a0c90e5c52522c945?a=0x0AA3B08BAFA836DAE445308D7F162aC8d5D8BEb3
    token = "0x389999216860ab8e0175387a0c90e5c52522c945"
    wallet = "0x0AA3B08BAFA836DAE445308D7F162aC8d5D8BEb3"

    url = "https://api.tokenbalance.com/token/"+token+"/"+wallet
    response = make_request(url)
    quantita = float(response["balance"])
    print("quantita", quantita)

    #https://www.dextools.io/app/uniswap/pair-explorer/0x854373387e41371ac6e307a1f29603c6fa10d872
    dextools_address = "0x854373387e41371ac6e307a1f29603c6fa10d872"
    url = "https://www.dextools.io/app/uniswap/pair-explorer/" + dextools_address

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent={0}'.format(user_agent))
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

    driver_path = os.environ.get('CHROMEDRIVER_PATH')
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)

    element_present = EC.element_to_be_clickable((By.CSS_SELECTOR, "li.pair-price"))
    WebDriverWait(driver, 7).until(element_present)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # <li _ngcontent-idv-c93="" class="ng-tns-c93-2 pair-price text-right text-success ng-star-inserted" style=""> ... </li>
    price = soup.find("li", attrs={"class": "pair-price"}).find("span")
    price = price.text[1:]

    totale = float(price) * float(quantita)
    print("totale", totale)
    driver.quit()

    result = {
        "quantita": quantita,
        "totale": totale
    }

    return result

def get_data():
    feg_res = feg()
    gas_res = gas_price()

    print("feg_result", feg_res)
    print("gas_result", gas_res)

    roi = (feg_res["totale"] - gas_res["transaction_cost"]) / 3
    roi = usd_to_eur(roi)

    locale.setlocale(locale.LC_ALL, 'de_DE')

    monke = False
    if roi >= 116:
        monke = True

    result = {
        "quantita": "" + locale.format_string('%.2f', feg_res["quantita"], True),
        "totale": "{0:.2f}€".format(feg_res["totale"]),
        "tempo": str(gas_res["time_to_complete"])+"min",
        "costo": "{0:.2f}€".format(usd_to_eur(gas_res["transaction_cost"])),
        "roi": "{0:.2f}€".format(roi),
        "data": datetime.datetime.now(),
        "monke": monke
    }
    
    # we did it boys
    if roi >= 116:
        result["roi"] = result["roi"] + " \U0001F680\U0001F680\U0001F680"

    database.write(result)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=5)
def timed_job():
    print("Eseguo wallet_info ", datetime.datetime.now())
    get_data()

'''
# testing stuff
get_data()
print(database.read())
'''