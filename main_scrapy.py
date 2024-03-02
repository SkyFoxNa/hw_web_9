import json

import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field

from seed import load_authors_from_file, load_qoutes_from_file
from conects import connect_to_mongodb


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


class QuoteItem(Item):
    tags = Field()
    author = Field()
    quote = Field()


class DataPipline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        data = ItemAdapter(item)

        if 'fullname' in data.keys():
            self.authors.append(dict(data))

        if 'quote' in data.keys():
            self.quotes.append(dict(data))

    def close_spider(self, spider):
        # Запис до файлів json
        with open('quotes.json', 'w', encoding='utf-8') as fd:
            json.dump(self.quotes, fd, ensure_ascii=False, indent=2)

        with open('authors.json', 'w', encoding='utf-8') as fd:
            json.dump(self.authors, fd, ensure_ascii=False, indent=2)


class MainSpider(scrapy.Spider):
    name = "get_quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {DataPipline: 300}}

    # Робота на основной сторінці
    def parse(self, response, **kwargs):
        for qt in response.xpath("/html//div[@class='quote']"):
            # Шукаємо та тягнемо теги
            tags = qt.xpath("div[@class='tags']/a/text()").extract()
            # Шукаємо та тягнемо автора
            author = qt.xpath("span/small[@class='author']/text()").get().strip()
            # Прибираємо -
            author = author.replace("-", " ")
            # Шукаємо та тягнемо цитати
            quote = qt.xpath("span[@class='text']/text()").get().strip()
            # Прибираємо “
            quote = quote.replace('“', "").replace("”", "")

            yield QuoteItem(quote=quote, author=author, tags=tags)
            # Робимо перехід на сторінку автора
            yield response.follow(url=self.start_urls[0] + qt.xpath("span/a/@href").get(), callback=self.author_parse)

        # пошук інших сторінок
        next_link = response.xpath("/html//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)

    # Робота зі сторінкою автора
    def author_parse(self, response, **kwargs):
        content = response.xpath("/html//div[@class='author-details']")
        # Беремо ПІБ автора
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        # Прибираємо -
        fullname = fullname.replace("-", " ")
        # Беремо дату народження
        born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        # Беремо місце народження
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        # Беремо біографію
        description = content.xpath("div[@class='author-description']/text()").get().strip()
        yield AuthorItem(fullname=fullname, born_date=born_date, born_location=born_location, description=description)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(MainSpider)
    process.start()

    # Беремо з попереднього ДЗ
    # Завантаження даних з файлів у відповідні колекції MongoDB
    connect_to_mongodb()  # Підключення до  MongoDB з файлу connects
    load_authors_from_file('authors.json')
    load_qoutes_from_file('quotes.json')
