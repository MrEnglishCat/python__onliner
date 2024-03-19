import json
import time
from pprint import pprint

import requests
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseParser(ABC):
    MAIN_URL = 'https://catalog.onliner.by/notebook'
    __PAGE_COUNTER = 1
    # __PAGE_COUNTER = 219
    __PATTERN_DATETIME = r'%Y-%m-%d %H:%M %z'
    __TIMEZONE_OFFSET = 3
    __ERRORS_SUCCESS = []
    __ALERTS = {
        'error': '[ERROR]',
        'info': 'INFO',
        'message_parser':{
            'False': 'Запись обработана/ Цена не найдена, вероятно товар снят с производства!',
            'True': 'Запись обработана',
            'error': 'Запись не обработана',

        },
        'db':{
            'success': 'Данные записаны в БД',
            'error':'Возникла ошибка при записи в БД'
        }
    }
    __IS_ALL_DATA_COLLECTED = False
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
        return type(self).__ERRORS_SUCCESS

    def insert_to_db(self, connection, data):
        cursor = connection.cursor()
        try:
            cursor.execute(
                f"""INSERT INTO notebook_onlinermodel (url, notebook_name, notebook_description, notebook_price, notebook_all_price_link, parse_datetime, is_discontinued)
                   VALUES 
                    {data}
                """
            )
            connection.commit()
            type(self).__ERRORS_SUCCESS.append(
                f'[PAGE {type(self).__PAGE_COUNTER-1}] [{type(self).__ALERTS.get("info")}] {type(self).__ALERTS.get("db").get("success")}'
            )
        except:
            print(data)
            type(self).__ERRORS_SUCCESS.append(
                f'[PAGE {type(self).__PAGE_COUNTER-1}] {type(self).__ALERTS.get("error")} {type(self).__ALERTS.get("db").get("error")}'
            )

    def get_urls_from_page(self, url: str) -> list:
        result = {}
        while True:
            response = requests.get(f"{url}?page={type(self).__PAGE_COUNTER}", headers=type(self).__HEADERS)
            soup = BeautifulSoup(response.content, 'lxml')
            if type(self)._check_pagination(soup):
                break
            else:
                soup.find_all('div', class_='catalog-form__offers-unit catalog-form__offers-unit_primary')
                page_links = soup.find_all('a', class_='catalog-form__preview')
                type(self).__PAGE_COUNTER += 1
                result.update(
                    {
                        type(self).__PAGE_COUNTER: page_links
                    }
                )
            #  break ниже для парсинга одной страницы
            break
        # return page_links
        return result

    def get_data_from_page(self, urls: list):
        result = []
        __counter = 1
        __total_counter = len(urls)
        for url in urls:
            try:
                resp = requests.get(url.get('href'), headers=type(self).__HEADERS)
                soup = BeautifulSoup(resp.content, 'lxml')
                notebook_name = soup.find('h1', class_='catalog-masthead__title js-nav-header').text
                notebook_description = soup.find('div', class_='offers-description__specs').find('p').text
                prices = soup.find('a',
                                   class_='offers-description__link offers-description__link_nodecor js-description-price-link')
                if prices:
                    notebook_price = prices.text
                    notebook_all_price_link = prices.get('href')
                    is_discontinued = False
                else:
                    type(self).__ERRORS_SUCCESS.append(
                        f"[PAGE {type(self).__PAGE_COUNTER-1}] [{type(self).__ALERTS.get('info')} {__counter}/{__total_counter}] {type(self).__ALERTS.get('message_parser').get('False')}"
                    )
                    type(self).__IS_ALL_DATA_COLLECTED = True
                    notebook_price = '0'
                    notebook_all_price_link = url.get('href')
                    is_discontinued = True

                result.append(
                    {
                        'url': url.get('href'),
                        'notebook_name': notebook_name.strip(),
                        'notebook_description': notebook_description.strip(),
                        'notebook_price': notebook_price.strip(),
                        'notebook_all_price_link': notebook_all_price_link,
                        'is_discontinued': is_discontinued
                    }
                )

                if not type(self).__IS_ALL_DATA_COLLECTED:
                    type(self).__ERRORS_SUCCESS.append(
                        f"[PAGE {type(self).__PAGE_COUNTER-1}] [{type(self).__ALERTS.get('info')} {__counter}/{__total_counter}] {type(self).__ALERTS.get('message_parser').get('True')}"
                    )
                type(self).__IS_ALL_DATA_COLLECTED = False
                __counter += 1
            except Exception as e:
                result.append(
                    {
                        'url': url.get('href'),
                        'notebook_name': '',
                        'notebook_description': '',
                        'notebook_price': '0',
                        'notebook_all_price_link': url.get('href'),
                        'is_discontinued': True
                    }
                )
                type(self).__ERRORS_SUCCESS.append(
                    f"[PAGE {type(self).__PAGE_COUNTER-1}] [{type(self).__ALERTS.get('error')} {__counter}/{__total_counter}] {type(self).__ALERTS.get('message_parser').get('error')}"
                )
                __counter += 1

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
            is_discontinued = item['is_discontinued']
            result.append(
                f"('{url}', '{notebook_name}', '{notebook_description}', {notebook_price}, '{notebook_all_price_link}', '{parse_datetime}', {is_discontinued})"
            )
        return ', '.join(result)

    @staticmethod
    def _check_pagination(bs4_object):
        message = 'Упс! У нас нет таких товаров, попробуйте изменить условия поиска'
        class_ = 'catalog-message__description catalog-message__description_primary catalog-message__description_base-alter'

        # bs4_object.find('div', class_=class_).text.strip() == message
        #

        if bool(bs4_object.find('div', class_=class_)):
            return True
        else:
            return False

    def write_to_json(self, filepath:str, filename:str, data):
        import json, os
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(f'{filepath}/{filename}', 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=True, indent=3)

    def run(self):
        import json
        urls_from_page = self.get_urls_from_page(self.MAIN_URL)
        for page, urls in urls_from_page.items():
            raw_data = self.get_data_from_page(urls)
            self.write_to_json(f'notebook/parser/data/json', f'{type(self).__PAGE_COUNTER-1}_data.json', raw_data)
            data_for_insert_to_db = self._parse_data_result(raw_data)
            connection = self.connect_to_db()
            self.create_table_db(connection)
            self.insert_to_db(connection, data_for_insert_to_db)
        return self.get_errors
