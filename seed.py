import json

from mongoengine.errors import NotUniqueError

from models import Author, Quote


def load_authors_from_file(filename):
    with open(filename, encoding = 'utf-8') as field:
        data_authors = json.load(field)
        for el in data_authors:
            try :
                author = Author(fullname = el.get('fullname'), born_date = el.get('born_date'),
                                born_location = el.get('born_location'), description = el.get('description'))
                author.save()
            except NotUniqueError :
                print(f"Автор вже існує: {el.get('fullname')}")


def load_qoutes_from_file(filename):
    with open(filename, encoding = 'utf-8') as field:
        data_qoutes = json.load(field)
        for el in data_qoutes:
            author, *_ = Author.objects(fullname = el.get('author'))
            quote = Quote(quote = el.get('quote'), tags = el.get('tags'), author = author)
            quote.save()


if __name__ == '__main__':
    pass
