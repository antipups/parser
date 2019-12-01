import requests


def encode_from_html(string):   # перекодировка из html символов в обычные
    return ''.join(chr(int(x[-4:])) for x in string.split(';') if len(x) > 1)


def parse(url):
    """
        Первая часть функции, парсинг самого подкаста, а именно:
        его названия;       # есть всегда, но может быть в html спецсимволах, посему сделана функция
        описания;           # есть всегда
        картинки;           # есть всегда
        ключевых слов;      # может и не быть, посему есть проверка, тоже может быть в html спецсимволах
    """
    html = requests.get(url).text
    # находим название подкаста
    title_of_podcast = html[html.find('<title>') + 7: html.find('</title>')]
    if title_of_podcast.find('#') > -1:  # если встретили спецсимволы html
        title_of_podcast = encode_from_html(title_of_podcast)

    # находим описание подкаста
    description_of_podcast = html[html.find('<description>') + 13: html.find('</description>')]
    if description_of_podcast.find('<![CDATA[') > -1:  # если есть cdata (не читаемая интерпр. хуйня)
        description_of_podcast = description_of_podcast[
                                 description_of_podcast.find('<![CDATA[') + 9: description_of_podcast.find(']]>')]

    # находим картинку подкаста
    image_of_podcasts = html[html.find('<image>') + 7: html.find('</image>')]
    image_of_podcasts = image_of_podcasts[image_of_podcasts.find('<url>') + 5: image_of_podcasts.find('</url>')]

    # находим ключевые слова если они есть
    keyword_of_podcasts = str()
    if html.find('keywords>') > -1:
        temp_html = html[html.find('keywords>') + 9:]  # временная срезка, для нахождения ключ. слов
        keyword_of_podcasts += temp_html[: temp_html.find('</')]
        new_keywords = str()
        for word in keyword_of_podcasts.split(','):
            if word.find('#') > -1:
                new_keywords += encode_from_html(word) + ', '
            else:
                new_keywords += word + ', '
        keyword_of_podcasts = new_keywords

    print(title_of_podcast, description_of_podcast, image_of_podcasts, keyword_of_podcasts)



if __name__ == '__main__':
    parse('https://feeds.simplecast.com/CPNlXNwD')
    parse('https://podster.fm/rss.xml?pid=20066')
    parse('https://podster.fm/rss.xml?pid=29605')
    parse('https://meduza.io/rss/podcasts/peremotka')
    parse('https://mojomedia.ru/feed-podcasts/rebyata-my-potrahalis')
