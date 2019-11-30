import re
import requests
from bs4 import BeautifulSoup


def parse_from_mojomedia(url):
    html = requests.get(url).text
    print(html)


def parse_from_simplecast(url):
    pass


def parse_from_meduza(url):
    pass


def parse_from_podster(url):
    pass


def change(url):
    if url.find('mojomedia') > -1:
        parse_from_mojomedia(url)
    elif url.find('feeds') > -1:
        parse_from_simplecast(url)
    elif url.find('meduza') > -1:
        parse_from_meduza(url)
    elif url.find('podster') > -1:
        parse_from_podster(url)


if __name__ == '__main__':
    change('https://mojomedia.ru/feed-podcasts/rebyata-my-potrahalis')
