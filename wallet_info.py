from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from currency_converter import CurrencyConverter
import locale
from os import environ

def feg():
    #https://etherscan.io/token/0x389999216860ab8e0175387a0c90e5c52522c945?a=0x0AA3B08BAFA836DAE445308D7F162aC8d5D8BEb3
    token = "0x389999216860ab8e0175387a0c90e5c52522c945"
    wallet = "0x0AA3B08BAFA836DAE445308D7F162aC8d5D8BEb3"
    headers = requests.utils.default_headers()

    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'})

    url = "https://api.tokenbalance.com/token/"+token+"/"+wallet
    response = requests.get(url, headers=headers).json()
    print("Risposta tokenbalance:", response)
    quantita = float(response["balance"])

    #https://www.dextools.io/app/uniswap/pair-explorer/0x854373387e41371ac6e307a1f29603c6fa10d872
    dextools_address = "0x854373387e41371ac6e307a1f29603c6fa10d872"
    url = "https://www.dextools.io/app/uniswap/pair-explorer/" + dextools_address

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent={0}'.format(user_agent))
    if environ.get('GOOGLE_CHROME_BIN') is None:
        options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    else:
        options.binary_location = environ.get('GOOGLE_CHROME_BIN')

    driver_path = environ.get('CHROMEDRIVER_PATH')
    driver = None
    if driver_path is None:
        driver_path = ".\chromedriver.exe"
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
    else:
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)

    element_present = EC.element_to_be_clickable((By.CSS_SELECTOR, "li.pair-price"))
    WebDriverWait(driver, 7).until(element_present)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # <li _ngcontent-idv-c93="" class="ng-tns-c93-2 pair-price text-right text-success ng-star-inserted" style=""> ... </li>
    price = soup.find("li", attrs={"class": "pair-price"}).find("span")
    price = price.text[1:]

    totale = float(price) * float(quantita)
    driver.quit()

    c = CurrencyConverter()
    totale = c.convert(totale, 'USD', 'EUR')

    locale.setlocale(locale.LC_ALL, 'de_DE')

    result = {
        "quantita": "" + locale.format_string('%.2f', quantita, True),
        "totale": "{0:.2f}€".format(totale)
    }

    # we did it boys
    if totale >= 350:
        result["totale"] = result["totale"] + " \U0001F680\U0001F680\U0001F680"

    return result