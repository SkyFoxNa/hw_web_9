import json
import requests
from bs4 import BeautifulSoup

from seed import load_authors_from_file, load_qoutes_from_file
from conects import connect_to_mongodb

start_url = "https://quotes.toscrape.com/"


def process_item(quote_item, author_item, quotes_data, authors_data):
    quotes_data.append({
        'tags': quote_item['tags'],
        'author': quote_item['author'],
        'quote': quote_item['quote'],
    })

    authors_data.append({
        'fullname': author_item['fullname'],
        'born_date': author_item['born_date'],
        'born_location': author_item['born_location'],
        'description': author_item['description']
    })


# Робота на основной сторінці
def parse_quotes(soup, start_url, quotes_data, authors_data):
    for q in soup.find_all('div', class_ = 'quote'):
        # Шукаємо та тягнемо автора
        author = q.find('small', class_ = 'author').get_text().strip()
        # Шукаємо та тягнемо цитати
        quote = q.find('span', class_ = 'text').get_text().strip()
        # Прибираємо “
        quote = quote.replace('“', "").replace("”", "")
        # Шукаємо та тягнемо теги
        tags = [tag.get_text() for tag in q.find_all('a', class_ = 'tag')]
        quote_item = {'quote': quote, 'author': author, 'tags': tags}
        # Шукаємо перехід на сторінку автора
        author_link = start_url + q.find('a')['href']
        parse_author(author_link, quote_item, quotes_data, authors_data)


# Робота зі сторінкою автора
def parse_author(url, quote_item, quotes_data, authors_data):
    # Перехід на сторінку автора
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find('div', class_ = 'author-details')
    # Беремо ПІБ автора
    fullname = content.find('h3', class_ = 'author-title').get_text().strip()
    # Беремо дату народження
    born_date = content.find('span', class_ = 'author-born-date').get_text().strip()
    # Беремо місце народження
    born_location = content.find('span', class_ = 'author-born-location').get_text().strip()
    # Беремо біографію
    description = content.find('div', class_ = 'author-description').get_text().strip()

    # Прибираємо -
    fullname = fullname.replace("-", " ")

    author_item = {'fullname': fullname, 'born_date': born_date, 'born_location' : born_location,
                   'description': description}
    process_item(quote_item, author_item, quotes_data, authors_data)


# Запис до файлів json
def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main(start_url):
    authors_data = []
    quotes_data = []

    response = requests.get(start_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    parse_quotes(soup, start_url, quotes_data, authors_data)

    # пошук інших сторінок
    next_page = soup.find('li', class_ = 'next')
    while next_page:
        next_page_link = next_page.find('a')['href']
        response = requests.get(start_url + next_page_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        parse_quotes(soup, start_url, quotes_data, authors_data)
        next_page = soup.find('li', class_ = 'next')

    # Збереження результатів у json
    save_to_json(authors_data, 'authors.json')
    save_to_json(quotes_data, 'quotes.json')


if __name__ == '__main__':
    main(start_url)

    # Беремо з попереднього ДЗ
    # Завантаження даних з файлів у відповідні колекції MongoDB
    connect_to_mongodb()  # Підключення до  MongoDB з файлу connects
    load_authors_from_file('authors.json')
    load_qoutes_from_file('quotes.json')
