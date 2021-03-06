import ssl

import os.path
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
log_file = None


def checkAltex():
    status = "Nu au fost gasite produse conform criteriilor selectate."

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        "Upgrade-Insecure-Requests": "1", "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate"}
    r = requests.get("https://altex.ro/console-ps5/cpl/", headers=headers)
    r.encoding = 'utf-8'
    if status in r.text:
        in_stock = False
    else:
        in_stock = True

    return in_stock


h = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
]


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

    random_nr = str(random.randint(10 ** 16, 99999999999999999))
    ua = "Opera/%s.%s (Windows NT %s.%s) Presto/%s.%s.%s Version/%s.%s" \
 \
         % (random_nr[0], random_nr[1:3], random_nr[4], random_nr[5], random_nr[6], random_nr[7:9], random_nr[10:13],
            random_nr[13:15], random_nr[15:17])

    # headers = ({'User-Agent':
    #                 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

    headers = ({'User-Agent': ua})


    try:
        r = requests.get("https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/")

        if status in r.text:
            return False
        return checkPriceEmag(r)
    except Exception as e:
        print("Could not check Emag1 stock")
        print(e)


def checkEmag2():
    status = "Stoc epuizat"

    headers = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})


    try:
        r = requests.get("https://www.emag.ro/consola-playstation-5-so-9396406/pd/DNKW72MBM/")

        if status in r.text:
            return False
        return checkPriceEmag(r)
    except Exception as e:
        print("Could not check Emag2 stock")
        print(e)


def checkPriceEmag(r):
    try:
        global log_file

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
            debug_info = "[E STRIGATOR LA CER] " + debug_info + " pentru " + soup.find('h1',
                                                                                       class_='page-title').get_text().strip()
        else:
            debug_info += " NICEEEEEEEEEEEEEEEEE"
        print(debug_info)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        log_file.write("[{}] {}\n".format(current_time, debug_info))
        return price < max_price
    except Exception as e:
        print("Could not check price")
        print("Error: " + str(e))
        # print("Got: " + str(soup))


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
    except Exception as e:
        print('Could not send mail')
        print(e)


def start_mail_server():
    global log_file

    gmail_password = 'iskclablyfksortj'

    try:
        context = ssl.create_default_context()

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(gmail_user, gmail_password)

        server.sendmail(gmail_user, to[0], "Stock Checker Started")

        now = datetime.now()
        current_time = now.strftime("%H-%M-%S")

        if not os.path.exists('logs'):
            os.makedirs('logs')

        log_file = open(os.path.join("logs", "log{}.txt".format(current_time)), "w")
        print(log_file.name)

        return server
    except Exception as e:
        print('Could not start server')
        print(e)


def stop_mail_server(server):
    try:
        global log_file

        server.close()
        log_file.close()
        print("server closed")
    except Exception as e:
        print('Could not stop server')
        print(e)


def main():
    server = start_mail_server()
    try:
        index = 0
        while True:
            # if (checkAltex() == True):
            #     sendEmail("Altex", "https://altex.ro/console-ps5/cpl/")
            #     print("Altex: Item is in stock")
            # if (checkOrange() == True):
            #     sendEmail("Orange", "https://www.orange.ro/magazin-online/obiecte-conectate/consola-playstation-5")
            #     print("Orange: Item is in stock")
            if checkEmag1():
                sendEmail(server, "Emag",
                          "https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/")
                print("Emag: Item is in stock")
            if checkEmag2():
                sendEmail(server, "Emag", "https://www.emag.ro/consola-playstation-5-so-9396406/pd/DNKW72MBM/")
                print("Emag: Item is in stock")
            # if (checkGamers() == True):
            #     sendEmail("Gamers", "https://www.gamers.ro/playstation5/playstation-5-825gb")
            #     print("Gamers: Item is in stock")
            index += 1
            if index % 100 == 0:
                server.sendmail(gmail_user, to[0], "Stock Checker did {} checks".format(index))

            time.sleep(random.randint(30, 60))
    except KeyboardInterrupt:
        print("stopped")
    finally:
        stop_mail_server(server)


if __name__ == "__main__":
    main()