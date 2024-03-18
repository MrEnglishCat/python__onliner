import time
import requests
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseParser(ABC):
    URL = 'https://catalog.onliner.by/notebook'
    __PATTERN_DATETIME = r'%Y-%m-%d %H:%M %z'
    __TIMEZONE_OFFSET = 3
    __ERRORS_SUCCESS = []
    __ERRORS = {
        'error': '[ERROR]',
        'info': 'INFO'
    }
    __HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"'
    }

    @abstractmethod
    def connect_to_db(self):
        pass

    @abstractmethod
    def create_table_db(self, connection):
        pass

    @property
    def get_errors(self):
        return BaseParser.__ERRORS_SUCCESS

    def insert_to_db(self, connection, data):
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"""INSERT INTO notebook_onlinermobel (url, notebook_name, notebook_description, notebook_price, notebook_all_price_link, parse_datetime)
                   VALUES 
                    {data}
                """
            )
            connection.commit()
        except:
            BaseParser.__ERRORS_SUCCESS.append(
                f'{BaseParser.__ERRORS.get("error")} Возникла ошибка при записи в БД'
            )


    def get_urls_from_page(self, url: str) -> list:

        response = requests.get(url, headers=BaseParser.__HEADERS)
        soup = BeautifulSoup(response.content, 'lxml')
        soup.find_all('div', class_='catalog-form__offers-unit catalog-form__offers-unit_primary')

        page_links = soup.find_all('a', class_='catalog-form__preview')

        return page_links

    def get_data_from_page(self, urls: list):
        result = []
        __counter = 0
        __total_counter = len(urls)
        for url in urls:
            try:
                resp = requests.get(url.get('href'), headers=BaseParser.__HEADERS)
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

                BaseParser.__ERRORS_SUCCESS.append(
                    f"[{BaseParser.__ERRORS.get('info')} {__counter}/{__total_counter}] Запись обработана"
                )
            except:
                result.append(
                    {
                        'url': url.get('href'),
                        'notebook_name': '',
                        'notebook_description': '',
                        'notebook_price': '',
                        'notebook_all_price_link': ''
                    }
                )
                BaseParser.__ERRORS_SUCCESS.append(
                    f"[{BaseParser.__ERRORS.get('error')} {__counter}/{__total_counter}] Запись не обработана"
                )
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
        return self.get_errors