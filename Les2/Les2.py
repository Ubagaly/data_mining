import requests
import datetime as dt
from datetime import timedelta
import time
import bs4
from urllib.parse import urljoin
import pymongo

MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,}

class StatusCodeError(Exception):
    def __init__(self, txt):
        self.txt = txt

class MagnitParse:

    def __init__(self, start_url, mongo_db):
        self.start_url = start_url
        self.db = mongo_db

    def __get_soup(self, url) -> bs4.BeautifulSoup:
        while True:
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    raise StatusCodeError(f'status {response.status_code}')
                return bs4.BeautifulSoup(response.text, 'lxml')
            except (requests.exceptions.ConnectTimeout,
                    StatusCodeError, ConnectionError):
                time.sleep(0.1)

    def parse(self):
        soup = self.__get_soup(self.start_url)
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_tag in catalog_main.find_all("a", recursive=False):
            try:
                yield self.product_parse(product_tag)
            except AttributeError:
                pass

    def product_parse(self, product_tag):
        product_result = {
            "url": None,
            "promo_name": None,
            "product_name": None,
            "old_price": None,
            "new_price": None,
            "image_url": None,
            "date_from": None,
            "date_to": None,
        }
        product_result["url"] = urljoin(self.start_url, product_tag.attrs.get("href"))
        product_result["promo_name"] = product_tag.find("div", attrs={"class": "card-sale__header"}).text
        product_result["product_name"] = product_tag.find("div", attrs={"class": "card-sale__title"}).text
        product_result["old_price"] = self.price(product_tag.find("div", attrs={"class": "label__price_old"}))
        product_result["new_price"] = self.price(product_tag.find("div", attrs={"class": "label__price_new"}))
        product_result["image_url"] = urljoin(self.start_url, product_tag.find("img").attrs.get("data-src"))
        product_result["date_from"] = self.data_from(product_tag.find("div", attrs={"class": "card-sale__date"}).text)
        product_result["date_to"] = self.data_to(product_tag.find("div", attrs={"class": "card-sale__date"}).text)

        return product_result
    
# т.к. в каталоге есть товары на которые "old_price" отсутствует, а "new_price" представлено в виде строки
    # с величиной скидки в %, решила обработать этот момент подозреваю, что это можно было обработать более корректно..
    def price(self, product):
        if product:
            price = product.text
            if price.find('%') == -1:
                  return float(price[1: -1].replace('\n', '.'))
            return price[1: -1]
        return None

    def data_from (self, text):
        data_list = text.replace("с ", "", 1).replace("\n", "").split("до")
        temp_data = data_list[0].split()
        return dt.datetime(
                     year=dt.datetime.now().year,
                     day=int(temp_data[0]),
                     month=MONTHS[temp_data[1][:3]],
                     )

# немного помучилась, чтобы год корректно отображася
    def data_to (self, text):
        data_list = text.replace("с ", "", 1).replace("\n", "").split("до")
        temp_data = data_list[1].split()
        free_day = timedelta(days=3)
        year_day = timedelta(days=366)
        datas_to = dt.datetime(
                     year=dt.datetime.now().year,
                     day=int(temp_data[0]),
                     month=MONTHS[temp_data[1][:3]],
                     )
        if datas_to + free_day > dt.datetime(year=dt.datetime.now().year, day=31, month=12):
            return datas_to
        return datas_to +year_day

    def run(self):
        for product in self.parse():
            collection = self.db["magnit"]
            collection.insert_one(product)

start_url = "https://magnit.ru/promo/?geo=moskva"
if __name__ == '__main__':
    database = pymongo.MongoClient('mongodb://localhost:27017')['magnit_parse']
    parser = MagnitParse(start_url, database)
    parser.run()