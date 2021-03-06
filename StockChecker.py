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
from email.message import EmailMessage
from datetime import datetime

max_price = 3000
log_file = None
server = None

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

class NoPriceFoundException(Exception):
    pass


def checkEMAG():
    links = ["https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/",
             "https://www.emag.ro/consola-playstation-5-so-9396406/pd/DNKW72MBM/"]

    for link in links:
        if checkEMAGLink(link):
            sendEmail(server, "eMAG",
                      "https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/")
            print("Emag: Item is in stock")

def checkEMAGLink(link):
    global server
    status = "Stoc epuizat"

    random_nr = str(random.randint(10 ** 16, 99999999999999999))
    ua = "Opera/%s.%s (Windows NT %s.%s) Presto/%s.%s.%s Version/%s.%s" \
 \
         % (random_nr[0], random_nr[1:3], random_nr[4], random_nr[5], random_nr[6], random_nr[7:9], random_nr[10:13],
            random_nr[13:15], random_nr[15:17])

    # headers = ({'User-Agent':
    #                 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

    headers = ({'User-Agent': ua})

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        'referer': 'https://www.google.com/'
    }

    try:
        r = requests.get(link, headers=header)

        if status in r.text:
            return False

        ans = checkPriceEMAG(r)

        if ans == 'Exception':
            msg = EmailMessage()
            msg.set_content(
                "Could not check price on link: {}\nPlease inspect the problem!\n\nTimestamp: {}".format(link,getTimeStamp()))

            msg['Subject'] = 'Problem occured'
            msg['From'] = "stockcecar@gmail.com"
            msg['To'] = "razvanrtr@outlook.com"

            server.send_message(msg)

            return

        return ans

    except NoPriceFoundException:
        msg = EmailMessage()
        msg.set_content(
            "Could not check price on link: {}\nPlease inspect the problem!\n\nTimestamp: {}".format(link,
                                                                                                     getTimeStamp()))

        msg['Subject'] = 'Problem occured'
        msg['From'] = "stockcecar@gmail.com"
        msg['To'] = "razvanrtr@outlook.com"

        server.send_message(msg)

    except Exception as e:
        print("Could not check eMAG stock")
        print("Error: {}".format(e))


def checkPriceEMAG(responseBody):
    try:
        global log_file

        soup = BeautifulSoup(responseBody.content, features="lxml")
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

        log_file.write("[{}] {}\n".format(getTimeStamp(), debug_info))
        return price < max_price

    except Exception as e:
        print("Could not check price")
        print("Error: " + str(e))
        # print("Got: " + str(soup))
        # return 'Exception'
        raise NoPriceFoundException()

gmail_user = 'stockcecar@gmail.com'
to = [
    "razvanrtr@outlook.com",
    "ioanaa.alexandru98@gmail.com",
    "chris.luntraru@gmail.com"

]
# "ioanaa.alexandru98@gmail.com",
# "chris.luntraru@gmail.com"

def getTimeStamp():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

def sendEmail(site, link):
    try:
        global  server

        msg = EmailMessage()

        subject = 'Found PS5 on {}'.format(site)
        mesaj = "Link: {}\nHURRY UP!!!\n\nTimestamp: {}".format(link, getTimeStamp())

        msg.set_content(mesaj)
        msg['Subject'] = subject
        msg['From'] = "stockcecar@gmail.com"

        for i in to:
            msg['To'] = i
            server.send_message(msg)

    except Exception as e:
        print('Could not send mail')
        print(e)


def start_mail_server():
    global log_file
    global server

    gmail_password = 'iskclablyfksortj'

    try:
        context = ssl.create_default_context()

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(gmail_user, gmail_password)

        current_time = getTimeStamp()

        msg = EmailMessage()
        msg.set_content("Timestamp: {}".format(current_time))

        msg['Subject'] = 'StockChecker started'
        msg['From'] = "stockcecar@gmail.com"
        msg['To'] = "razvanrtr@outlook.com"

        server.send_message(msg)


        if not os.path.exists('logs'):
            os.makedirs('logs')

        log_file = open(os.path.join("logs", "log{}.txt".format(current_time.replace(':','-'))), "w")

        return server
    except Exception as e:
        print('Could not start server')
        raise e


def stop_mail_server():
    try:
        global log_file
        global server

        filename = log_file.name
        log_file.close()

        f = open(filename, "r")

        msg = EmailMessage()
        msg.set_content("Timestamp: {}".format(getTimeStamp()))
        msg.add_attachment(f.read(), filename="log_file.txt")

        msg['Subject'] = 'StockChecker stopped'
        msg['From'] = "stockcecar@gmail.com"
        msg['To'] = "razvanrtr@outlook.com"

        server.send_message(msg)

        server.close()
        f.close()
        print("server closed")
    except Exception as e:
        print('Could not stop server')
        print(e)
        raise e


def main():
    global server
    server = start_mail_server()
    try:
        index = 0
        while True:
            checkEMAG()

            index += 1
            if index % 50 == 0:
                msg = EmailMessage()
                msg.set_content( "StockChecker did {} checks".format(index))

                msg['Subject'] = 'Update'
                msg['From'] = "stockcecar@gmail.com"
                msg['To'] = "razvanrtr@outlook.com"

                server.send_message(msg)

            time.sleep(random.randint(30, 60))
    except KeyboardInterrupt:
        print("stopped")
    finally:
        stop_mail_server()


if __name__ == "__main__":
    main()