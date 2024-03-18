import time
from datetime import datetime, timezone, timedelta
from pprint import pprint

import requests

from abc import ABC, abstractmethod

import tzlocal
from bs4 import BeautifulSoup


class BaseParser(ABC):
    URL = 'https://catalog.onliner.by/notebook'
    __PATTERN_DATETIME = r'%Y-%m-%d %H:%M %z'
    __TIMEZONE_OFFSET = 3

    @abstractmethod
    def connect_to_db(self):
        pass

    @abstractmethod
    def create_table_db(self, connection):
        pass

    def insert_to_db(self, connection, data):
        cursor = connection.cursor()
        cursor.execute(
            f"""INSERT INTO notebook (url, notebook_name, notebook_description, notebook_price, notebook_all_price_link, parse_datetime)
               VALUES 
                {data}
            """
        )
        connection.commit()

    def get_urls_from_page(self, url: str) -> list:

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        soup.find_all('div', class_='catalog-form__offers-unit catalog-form__offers-unit_primary')

        page_links = soup.find_all('a', class_='catalog-form__preview')

        return page_links

    def get_data_from_page(self, urls: list):
        result = []
        __counter = 0
        __total_counter = len(urls)
        for url in urls:
            resp = requests.get(url.get('href'))
            soup = BeautifulSoup(resp.content, 'lxml')
            notebook_name = soup.find('h1', class_='catalog-masthead__title js-nav-header').text
            notebook_description = soup.find('div', class_='offers-description__specs').find('p').text
            prices = soup.find('a',
                               class_='offers-description__link offers-description__link_nodecor js-description-price-link')
            notebook_price = prices.text
            notebook_all_price_link = prices.get('href')
            result.append(
                {
                    'url': url.get('href'),
                    'notebook_name': notebook_name.strip(),
                    'notebook_description': notebook_description.strip(),
                    'notebook_price': notebook_price.strip(),
                    'notebook_all_price_link': notebook_all_price_link
                }
            )
            __counter += 1
            print(f"[INDO {__counter}/{__total_counter}] Запись обработана")
        return result

    @staticmethod
    def _parse_data_result(data: list[dict]) -> str:
        result = []

        for item in data:
            url = item['url']
            notebook_name = item['notebook_name']
            notebook_description = item['notebook_description']
            notebook_price = item['notebook_price'].strip('.').replace(',', '.')
            notebook_price = float(
                ''.join(filter(lambda char: char if char.isdigit() or char in '.,' else '', notebook_price)))
            notebook_all_price_link = item['notebook_all_price_link']
            parse_datetime = datetime.utcnow()
            result.append(
                f"('{url}', '{notebook_name}', '{notebook_description}', '{notebook_price}', '{notebook_all_price_link}', '{parse_datetime}')"
            )
        return ', '.join(result)

    def run(self):
        connection = self.connect_to_db()
        self.create_table_db(connection)
        urls_from_page = self.get_urls_from_page(self.URL)
        raw_data = self.get_data_from_page(urls_from_page)
        data_for_insert_to_db = self._parse_data_result(raw_data)
        self.insert_to_db(connection, data_for_insert_to_db)
