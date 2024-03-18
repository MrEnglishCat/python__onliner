import requests
from bs4 import BeautifulSoup


url = 'https://catalog.onliner.by/notebook'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')
soup.find_all('div', class_='catalog-form__offers-unit catalog-form__offers-unit_primary')

print(*soup, sep='\n')