import requests

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseParser(ABC):
    URL = 'https://catalog.onliner.by/notebook'
    @abstractmethod
    def connect_to_db(self):
        pass

    @abstractmethod
    def create_table_db(self, connection):
        pass

    def insert_to_db(self, connection):
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO notebook (url, notebook_name, notebook_description, notebook_price, notebook_all_price_link)
               VALUES 
            """
        )

    def get_urls_from_page(self, url: str) -> list:

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        soup.find_all('div', class_='catalog-form__offers-unit catalog-form__offers-unit_primary')

        page_links = soup.find_all('a', class_='catalog-form__preview')

        return page_links

    def get_data_from_page(self, urls: list):
        result = []
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
                    'url': url,
                    'notebook_name': notebook_name,
                    'notebook_description': notebook_description,
                    'notebook_price': notebook_price,
                    'notebook_all_price_link': notebook_all_price_link
                }
            )
        return result

    def run(self):
        connection = self.connect_to_db()
        self.create_table_db(connection)
        urls_from_page = self.get_urls_from_page(self.URL)
        data_for_send_to_db = self.get_data_from_page(urls_from_page)
        for item in data_for_send_to_db:
            pass
            # self.insert_to_db(connection, item)