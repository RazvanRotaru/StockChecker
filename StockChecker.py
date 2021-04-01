import ssl
import os.path
import requests
import time
import random
import urllib3
import smtplib

from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.message import EmailMessage
from datetime import datetime

max_price = 3000

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

#TODO add print function to write both to console and file

class StockChecker:
    def __init__(self):
        self.iter = 0
        self.__INT = 50  # iteration number threshold
        subfolder = 'logs'
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)
        self._log_file = open(os.path.join(subfolder, 'log{}.txt'.format(get_time_stamp().replace(':', '-'))), 'w')
        self.mail_handler = MailHandler()

    def __stop(self):
        filename = self._log_file.name
        self._log_file.close()
        self.mail_handler.stop_server(filename)

    def run(self):
        try:
            while True:
                self.__iteration_routine()
                self.__check_eMAG()
                time.sleep(random.randint(30, 60))
        except Exception:
            print("stopped")
        except KeyboardInterrupt:
            print("stopped by keyboard")
            self.__stop()

    def __iteration_routine(self):
        self.iter += 1

        iter_info = '\n----------------------------- ITERATION {} -----------------------------'.format(self.iter)
        print(iter_info)
        self._log_file.write(iter_info)

        if self.iter % self.__INT == 0:
            mail_prefab = self.mail_handler.mail_prefabs['update']
            self.mail_handler.notify(message=mail_prefab['message'](self.iter),
                                     subject=mail_prefab['subject'],
                                     debug_only=True)

    def __check_eMAG(self):
        links = ["https://www.emag.ro/consola-playstation-5-digital-edition-so-9396505/pd/DKKW72MBM/",
                 "https://www.emag.ro/consola-playstation-5-so-9396406/pd/DNKW72MBM/"]

        for link in links:
            if self.__check_eMAG_link(link):
                mail_prefab = self.mail_handler.mail_prefabs['found']
                self.mail_handler.notify(message=mail_prefab['message'](link),
                                         subject=mail_prefab['subject']('eMAG'))

                print("eMAG: Item is in stock")

    def __check_eMAG_link(self, link):
        status = "Stoc epuizat"

        random_nr = str(random.randint(10 ** 16, 99999999999999999))
        ua = "Opera/%s.%s (Windows NT %s.%s) Presto/%s.%s.%s Version/%s.%s" \
 \
             % (
                 random_nr[0], random_nr[1:3], random_nr[4], random_nr[5], random_nr[6], random_nr[7:9],
                 random_nr[10:13],
                 random_nr[13:15], random_nr[15:17])

        # headers = ({'User-Agent':
        #                 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

        headers = ({'User-Agent': ua})

        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            'referer': 'https://www.google.com/'
        }

        try:
            response = requests.get(link, headers=header)

            if status in response.text:
                return False

            ans = self.__check_eMAG_price(response)

            if ans == 'Exception':
                mail_prefab = self.mail_handler.mail_prefabs['error']
                self.mail_handler.notify(message=mail_prefab['message'](link),
                                         subject=mail_prefab['subject'],
                                         debug_only=True)
                return

            return ans

        except Exception as e:
            print("Could not check eMAG stock")
            print("Error: {}".format(e))

    def __check_eMAG_price(self, responseBody):
        try:
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

            price_info = '{:.2f}'.format(price)
            name_info = soup.find('h1', class_='page-title').get_text().strip()

            if price > max_price:
                debug_info = 'E STRIGATOR LA CER: {} for {}'.format(price_info, name_info)
            else:
                debug_info += 'FOUND {} at {}'.format(name_info, price_info)
            print(debug_info)

            self._log_file.write("[{}] {}\n".format(get_time_stamp(), debug_info))
            return price < max_price

        except Exception as e:
            print('Could not check price {}'.format(e))
            return 'Exception'
            # raise NoPriceFoundException(0735300875)


class MailHandler:

    def __init__(self):
        self.initialized = False
        self.__mails_sent = 0
        self._user = 'stockcecar@gmail.com'
        self.__password = 'iskclablyfksortj'
        self._receivers = ['razvanrtr@outlook.com',
                           'ioanaa.alexandru98@gmail.com',
                           'chris.luntraru@gmail.com']
        self._debuggers = [self._user,
                           'razvanrtr@outlook.com']
        self.mail_prefabs = {
            'found': {'message': self.format_found_message,
                      'subject': self.format_found_subject},
            'start': {'message': '',
                      'subject': 'StockChecker started'},
            'stop': {'message': '',
                     'subject': 'StockChecker stopped'},
            'update': {'message': self.format_update_message,
                       'subject': 'Update'},
            'error': {'message': self.format_error_message,
                      'subject': 'Error occurred'}
        }
        self.notify(subject=self.mail_prefabs['start']['subject'], debug_only=True)


        self.initialized = True

    def format_error_message(self, link):
        return 'Could not check price on link: {}\nPlease inspect the problem!\n\nTimestamp: {}'.format(link,
                                                                                                        get_time_stamp())

    def format_found_message(self, link):
        return 'Link: {}\nHURRY UP!!!\n\nTimestamp: {}'.format(link, get_time_stamp())

    def format_found_subject(self, site):
        return 'Found PS5 on {}'.format(site)

    def format_update_message(self, iterations):
        return "StockChecker did {} checks".format(iterations)

    def __connect_to_server(self):
        try:
            context = ssl.create_default_context()
            self._server = smtplib.SMTP('smtp.gmail.com', 587)
            self._server.ehlo()
            self._server.starttls(context=context)
            self._server.ehlo()
            self._server.login(self._user, self.__password)

        except Exception as e:
            print('Could not start server {}'.format(e))

    def stop_server(self, filename):
        try:
            self.notify(subject=self.mail_prefabs['stop']['subject'], filename=filename, debug_only=True)
            print("server closed")
        except Exception as e:
            print('Could not stop server {}'.format(e))

    def notify(self, message='', subject='', filename=None, debug_only=False):
        try:
            self.__connect_to_server()

            msg = EmailMessage()
            msg.set_content('{}\n\nTimestamp: {}'.format(message, get_time_stamp()))

            if filename is not None:
                file = open(filename, 'r')
                msg.add_attachment(file.read(), filename='log-file.txt')
                file.close()

            msg['Subject'] = subject
            msg['From'] = self._user

            receivers = self._debuggers if debug_only else self._receivers

            msg['To'] = receivers
            self._server.send_message(msg)

            self._server.quit()

        except Exception as e:
            print('Could not send mail: {}'.format(e))
            # raise e


class _NoPriceFoundException(Exception):
    pass


def get_time_stamp():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def main():
    stock_checker = StockChecker()
    stock_checker.run()


if __name__ == "__main__":
    main()
