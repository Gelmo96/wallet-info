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
                      'Chrome/50.0.2661.102 Safari/537.36',
        'referer': 'https://etherscan.io/'})

    '''
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    })
    
    headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36'})
    '''

    #pagina del token
    url = "https://etherscan.io/token/" + token
    print("Requesting url:", url)
    print("using headers:", headers)
    # richiesta pagina web
    response = requests.get(url, headers=headers)
    status = response.status_code
    print("Status code:", status)
    if not status < 400:
        raise Exception('Web request failed')
    # parsing html
    soup = BeautifulSoup(response.text, "lxml")

    #<div id="ContentPlaceHolder1_tr_tokenHolders">
    holders_list = soup.find("div", attrs={"id": "ContentPlaceHolder1_tr_tokenHolders"}).find("div", attrs={"class":"mr-3"})
    holders = holders_list.contents[0].strip()
    perc = holders_list.contents[1]["title"].split()[1].strip()

    url = "https://etherscan.io/token/" + token + "?a=" + wallet
    # richiesta pagina web
    html_content = requests.get(url, headers=headers).text
    # parsing html
    soup = BeautifulSoup(html_content, "lxml")

    #<div id="ContentPlaceHolder1_divFilteredHolderBalance" ... >
    quantita = soup.find("div", attrs={"id": "ContentPlaceHolder1_divFilteredHolderBalance"}).contents[2].split()[0].strip()
    quantita = float(quantita.replace(",",""))

    #<div id="ContentPlaceHolder1_divFilteredHolderValue" ... >
    totale = soup.find("div", attrs={"id": "ContentPlaceHolder1_divFilteredHolderValue"}).contents[4].split()[0]
    totale = float(totale[1:].strip())

    if totale == 0:
        #https://www.dextools.io/app/uniswap/pair-explorer/0x854373387e41371ac6e307a1f29603c6fa10d872
        dextools_address = "0x854373387e41371ac6e307a1f29603c6fa10d872"
        url = "https://www.dextools.io/app/uniswap/pair-explorer/" + dextools_address


        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('user-agent={0}'.format(user_agent))
        options.binary_location = environ['GOOGLE_CHROME_BIN']

        driver = webdriver.Chrome(execution_path=environ['CHROMEDRIVER_PATH'], options=options)
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

    locale.setlocale(locale.LC_ALL, 'German')
    '''
    print("Holders:\t" + holders,
            "\nPerc:\t\t" + perc,
            #"\nQuantità:\t{0:.2f}".format(quantita),
            "\nQuantità:\t" + locale.format_string('%.2f', quantita, True),
            "\nTotale:\t\t€{0:.2f}".format(totale))
    '''

    result = {
        "holders" : "" + holders,
        "perc": "" + perc,
        "quantita": "" + locale.format_string('%.2f', quantita, True),
        "totale": "{0:.2f}€".format(totale)
    }

    # we did it boys
    if totale >= 350:
        result["totale"] = result["totale"] + " \U0001F680\U0001F680\U0001F680"

    return result

'''
res = feg()
for key, item in res.items():
    print(key, item)
'''