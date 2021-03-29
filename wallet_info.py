import os
import locale
import database
import datetime
import math
import re
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

    return requests.get(url, headers=headers)


def make_selenium_request(url, css_selector):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 ' \
                 'Safari/537.36 '

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent={0}'.format(user_agent))
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

    driver_path = os.environ.get('CHROMEDRIVER_PATH')
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)

    if css_selector is not None:
        element_present = EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        WebDriverWait(driver, 7).until(element_present)
    result = driver.page_source
    driver.quit()

    return result


def eth_price():
    url = "https://etherscan.io/token/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

    # tentativo 1, scraping
    try:
        response = make_request(url)
        if response.ok:
            soup = BeautifulSoup(response.text, "lxml")

            # <div id="ContentPlaceHolder1_tr_valuepertoken" class="border-bottom pb-1 mb-3" style="margin-top:-6px;">
            # <span class="d-block">$1,560.2300</span>
            # </div>
            price_str = soup.find("div", attrs={"id": "ethPrice"}).find("span").contents[0].replace(",","")
            # numero di qualsiasi lunghezza con o senza punto decimale
            price = re.search("(\d*\.?\d+)", price_str).group()

            print("eth_price: ok da etherscan")

            return {
                "ok": True,
                "price": float(price)
            }
        else:
            print("eth_price: errore richiesta etherscan:\t", response.status_code)
    except:
        pass

    # tentativo 2: richiesta API defipulse
    try:
        key = os.environ.get('DEFIPULSE_KEY')
        url_2 = "https://data-api.defipulse.com/api/v1/dexag/markets?api-key=" + key
        response = make_request(url_2)
        json_data = response.json()
        print("eth_price: ok da API defipulse")
        return {
            "ok": True,
            "price": json_data["AG"]["ETH-USDC"]["ask"]
        }
    except:
        print("eth_price: errore richiesta defipulse:\t", response.text)
        pass


    #tentativo 3: scraping da dextools
    try:
        # https://www.dextools.io/app/uniswap/pair-explorer/0x854373387e41371ac6e307a1f29603c6fa10d872
        dextools_address = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"
        url = "https://www.dextools.io/app/uniswap/pair-explorer/" + dextools_address

        result = make_selenium_request(url, "li.pair-price")
        soup = BeautifulSoup(result, "lxml")

        # <li _ngcontent-idv-c93="" class="ng-tns-c93-2 pair-price text-right text-success ng-star-inserted" style=""> ... </li>
        price = soup.find("li", attrs={"class": "pair-price"}).find("span")
        price = price.text[1:]
        print("eth_price: ok da dextools")
        return {
            "ok": True,
            "price": price.replace(",","")
        }
    except:
        print("eth_price: errore richiesta defipulse:\t", response.status_code)
        pass

    # worst case scenario: ha fallito ogni richiesta
    print("eth_price: tutte le richieste fallite")
    return {
        "ok": False
    }


def gas_price():
    defipulse_key = os.environ.get('DEFIPULSE_KEY')
    url = "https://data-api.defipulse.com/api/v1/egs/api/ethgasAPI.json?api-key=" + defipulse_key

    '''
    # alternative 2
    etherscan_key = os.environ.get('ETHERSCAN_KEY')
    url = "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=" + etherscan_key
    '''

    '''
    # alternativa 3, scrape da
    https://etherscan.io/gastracker
    '''

    # gas API request
    gas_res = make_request(url).json()
    # costo medio di una quantità di gas in wei
    gwei_cost = gas_res["average"] / 10
    print("gas_price: costo di 1 gas in wei:\t", gwei_cost)
    # costo in eth di un gas
    eth = gwei_cost * (1 * 10 ** -9)
    # costo di tutta la transazione in gwei
    # 200.000 ammontare medio di gas per una transazione di FEG
    eth = float(eth * 200000)

    res_eth = eth_price()
    if not res_eth["ok"]:
        return {
            "ok": False
        }

    print("gas_price: risposta da eth_price:\t", res_eth["price"])

    transaction_cost = float(eth) * float(res_eth["price"])
    print("total transaction cost", transaction_cost)

    # tempo in minuti per completare la transazione
    time_to_complete = gas_res["avgWait"]
    print("gas_price: tempo esecuzione:\t", str(time_to_complete) + "minuti")

    return {
        "ok": True,
        "time_to_complete": time_to_complete,
        "transaction_cost": transaction_cost
    }


def usd_to_eur(cash):
    c = CurrencyConverter()
    cash = c.convert(cash, 'USD', 'EUR')
    return cash


def feg():
    # https://etherscan.io/token/0x389999216860ab8e0175387a0c90e5c52522c945?a=0x0AA3B08BAFA836DAE445308D7F162aC8d5D8BEb3
    token = "0x389999216860ab8e0175387a0c90e5c52522c945"
    wallet = "0x0AA3B08BAFA836DAE445308D7F162aC8d5D8BEb3"

    # tentativo 1: richiesta ad API tokenbalance
    tokenbalance_error = False
    url = "https://api.tokenbalance.com/token/" + token + "/" + wallet
    try:
        response = make_request(url)
        response = response.json()

        if response["error"]:
            print("feg: errore richiesta API tokenbalance")
            tokenbalance_error = True
        else:
            print("feg: quantita ok from tokenbalance")
            quantita = float(response["balance"])
    except:
        print("feg: errore richiesta tokenbalance API:\t", response.text)
        tokenbalance_error = True
        pass

    if tokenbalance_error:
        # tentativo 2: scraping da ehterscan.io
        url = "https://etherscan.io/token/" + token + "?a=" + wallet
        result = make_request(url)
        soup = BeautifulSoup(result.text, "lxml")
        # <div id="ContentPlaceHolder1_divFilteredHolderBalance" ...>
        balance = soup.find("div", attrs={"id": "ContentPlaceHolder1_divFilteredHolderBalance"}).contents[2]
        balance = balance.replace(",", "").split()[0]
        quantita = float(balance)

        if math.isnan(quantita) or quantita is 0:
            return {
                "ok": False
            }
        else:
            print("feg: quantita ok from etherscan")

    print("feg: quantita", quantita)

    # https://www.dextools.io/app/uniswap/pair-explorer/0x854373387e41371ac6e307a1f29603c6fa10d872
    dextools_address = "0x854373387e41371ac6e307a1f29603c6fa10d872"
    url = "https://www.dextools.io/app/uniswap/pair-explorer/" + dextools_address

    result = make_selenium_request(url, "li.pair-price")
    soup = BeautifulSoup(result, "lxml")

    # <li _ngcontent-idv-c93="" class="ng-tns-c93-2 pair-price text-right text-success ng-star-inserted" style=""> ... </li>
    price = soup.find("li", attrs={"class": "pair-price"}).find("span")
    price = price.text[1:]
    print("feg: costo singolo USD:\t", price)

    totale = float(price) * float(quantita)
    print("feg: totale nel wallet:\t", totale)

    result = {
        "ok": True,
        "quantita": quantita,
        "totale_usd": totale
    }

    return result


def get_data():

    feg_res = feg()
    if not feg_res["ok"]:
        return {
            "ok": False
        }

    gas_res = gas_price()
    if not gas_res["ok"]:
        return {
            "ok": False
        }

    print("get_data: feg_result:\t", feg_res)
    print("get_data: gas_result:\t", gas_res)

    locale.setlocale(locale.LC_ALL, 'de_DE')

    # data in formato UTC
    utc_data = datetime.datetime.utcnow()

    result = {
        "quantita": "" + locale.format_string('%.2f', feg_res["quantita"], True),
        "totale_eur": "{0:.2f}".format(usd_to_eur(feg_res["totale_usd"])),
        "totale_usd": "{0:.2f}".format(feg_res["totale_usd"]),
        "tempo": str(gas_res["time_to_complete"]),
        "gas_eur": "{0:.2f}".format(usd_to_eur(gas_res["transaction_cost"])),
        "gas_usd": "{0:.2f}".format(gas_res["transaction_cost"]),
        "data": utc_data
    }

    database.write(result)

    return {
        "ok": True
    }

'''
# testing stuff
get_data()
print(database.read())
'''
