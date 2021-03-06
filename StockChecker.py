import requests
import time
import random
import urllib3
# Import smtplib for the actual sending function
import smtplib
from bs4 import BeautifulSoup

# Import the email modules we'll need
from email.mime.text import MIMEText
from datetime import datetime

max_price = 3000

def checkAltex():
    status = "Nu au fost gasite produse conform criteriilor selectate."

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    r = requests.get("https://altex.ro/console-ps5/cpl/", headers = headers)
    r.encoding = 'utf-8'
    if status in r.text:
        in_stock = False
    else:
        in_stock = True

    return in_stock

def checkOrange():
    requests.packages.urllib3.disable_warnings()
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    try:
        requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass

    status = "Momentan produsul nu este"

    r = requests.get("https://www.orange.ro/magazin-online/obiecte-conectate/consola-playstation-5")
    r.encoding = 'utf-8'
    if status in r.text:
        in_stock = False
    else:
        in_stock = True

    return in_stock

def checkEmag1():
    status = "Stoc epuizat"
    try:
        r = requests.get("https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/")

        if status in r.text:
            return False
        return checkPriceEmag(r)
    except:
        print("Could not check Emag1 stock")

def checkEmag2():
    status = "Stoc epuizat"
    try:
        r = requests.get("https://www.emag.ro/consola-playstation-5-so-9396406/pd/DNKW72MBM/")

        if status in r.text:
            return False
        return checkPriceEmag(r)
    except:
        print("Could not check Emag2 stock")

def checkPriceEmag(r):
    try:
        soup = BeautifulSoup(r.content, features="lxml")
        product = soup.find('div', class_='main-product-form')
        if product is None:
            product = soup.find('form', class_='main-product-form')

        p = product.find('p', class_='product-new-price')

        p = p.get_text().strip()
        multiple = 'oferte de la'
        multiple_index = p.find(multiple)
        if multiple_index != -1:
            p = p[multiple_index + len(multiple):]
        price = int(''.join(filter(str.isdigit, p))) / 100
        debug_info = "{:.2f}".format(price)
        if price > max_price:
            debug_info = "[E STRIGATOR LA CER] " + debug_info + " pentru " + soup.find('h1', class_='page-title').get_text().strip()
        else:
            debug_info += " NICEEEEEEEEEEEEEEEEE"
        print(debug_info)
        return price < max_price
    except:
        print("Could not check price")


gmail_user = 'stockcecar@gmail.com'
to = [
    "razvanrtr@outlook.com",
    "ioanaa.alexandru98@gmail.com",
    "chris.luntraru@gmail.com"
]

def sendEmail(server, site, adresa):
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        mesaj = "\n" + "IN STOC: " + site + " LINK: " + adresa + " \n" + "TIMESTAMP: " + current_time

        for i in to:
            server.sendmail(gmail_user, i, mesaj)
    except:
        print ('Could not send mail')

def start_mail_server():
    gmail_password = 'SSFzsNAy6zVpDVt'

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)

        for i in to:
            server.sendmail(gmail_user, i, "Stock Checker Started")
        return server
    except:
        print('Could not start server')

def stop_mail_server(server):
    try:
        server.close()
        print("server closed")
    except:
        print('Could not stop server')

def main():
    server = start_mail_server()
    try:
        while True:
            # if (checkAltex() == True):
            #     sendEmail("Altex", "https://altex.ro/console-ps5/cpl/")
            #     print("Altex: Item is in stock")
            # if (checkOrange() == True):
            #     sendEmail("Orange", "https://www.orange.ro/magazin-online/obiecte-conectate/consola-playstation-5")
            #     print("Orange: Item is in stock")
            if (checkEmag1() == True):
                sendEmail(server, "Emag", "https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/")
                print("Emag: Item is in stock")
            if (checkEmag2() == True):
                sendEmail(server, "Emag", "https://www.emag.ro/consola-playstation-5-so-9396406/pd/DNKW72MBM/")
                print("Emag: Item is in stock")
            # if (checkGamers() == True):
            #     sendEmail("Gamers", "https://www.gamers.ro/playstation5/playstation-5-825gb")
            #     print("Gamers: Item is in stock")
            time.sleep(random.randint(30, 60))
    except KeyboardInterrupt:
        print("stopped")
    finally:
        stop_mail_server(server)


if __name__ == "__main__":
    main()