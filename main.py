import re
import requests
import util


def check_on_shit(string):      # чистим полученные строки от говна, типа сидата или спецсимволы хтмл
    if string.find('&#') > -1:
        string = encode_from_html(string)
    if string.find('<![CDATA[') > -1:   # чистим строку от cdata
        string = string[string.find('<![CDATA[') + 9: string.find(']]>')]
    if string.find('&lt') > -1:
        string = clear_from_decor(string)
    return string


def encode_from_html(string):   # перекодировка из html символов в обычные
    while re.search(r'&#\d{1,4};', string) is not None:
        swap_word = re.search(r'&#\d{1,4};', string)[0]    # копируем изменяемое слово
        if len(swap_word) != 7 or not 1040 <= int(swap_word[-5:-1]) <= 1103:  # все слова которые не буквы, меняем на пробел
            new_word = ' '
        else:
            new_word = chr(int(re.search(swap_word, string)[0][-5:-1]))
        string = re.sub(swap_word, new_word, string)
    return string


def clear_from_decor(string):   # чистим от плохой рссленты (c декором которая)
    while string.startswith('&lt;'):    # чистим от тега lt(он обычно всё инициирует, таблицы, картинки)
        string = string[string.find('&gt;') + 4:]
    while string.find('&lt;') > -1:     # опять таки чистим от него же но уже не в начале текста
        string = string[:string.find('&lt;')] + '\n' + string[string.find('&gt;') + 4:]
    return string


def convert_of_time(time):      # конвертация времени из секунд в часы
    return str(time // 3600) + ':' + str(time // 60 % 60) + ':' + str(time % 60)


def parse(url):
    """
        Первая часть функции, парсинг самого подкаста, а именно:
        его названия;       # есть всегда, но может быть в html спецсимволах, посему сделана функция
        описания;           # есть всегда
        картинки;           # есть всегда
        ключевых слов;      # может и не быть, посему есть проверка, тоже может быть в html спецсимволах
    """
    html = requests.get(url).content.decode('utf-8')
    # находим название подкаста
    title_of_podcast = html[html.find('<title>') + 7: html.find('</title>')]
    title_of_podcast = check_on_shit(title_of_podcast)

    # находим описание подкаста
    description_of_podcast = html[html.find('<description>') + 13: html.find('</description>')]
    description_of_podcast = check_on_shit(description_of_podcast)

    # находим картинку подкаста
    if html.find('<image>') > -1:
        image_of_podcasts = html[html.find('<image>') + 7: html.find('</image>')]
        image_of_podcasts = image_of_podcasts[image_of_podcasts.find('<url>') + 5: image_of_podcasts.find('</url>')]
    else:
        image_of_podcasts = html[html.find('image>') + 7:]
        image_of_podcasts = image_of_podcasts[image_of_podcasts.find('href="') + 6:]
        image_of_podcasts = image_of_podcasts[: image_of_podcasts.find('"')]

    # находим ключевые слова если они есть
    keyword_of_podcasts = str()
    if html.find('keywords>') > -1:     # если есть ключевые слова
        temp_html = html[html.find('keywords>') + 9:]   # временная срезка, для нахождения ключ. слов
        keyword_of_podcasts += temp_html[: temp_html.find('</')]
        keyword_of_podcasts = check_on_shit(keyword_of_podcasts)

    # находим автора, если он есть
    author_of_podcast = str()
    if html.find('author>') > -1:
        temp_code = html[html.find('author>') + 7:]
        author_of_podcast = check_on_shit(temp_code[:temp_code.find('</')])

    # находим категории если они есть
    categorys_of_podcast = str()
    subcategorys_of_podcast = str()
    while html.find('category ') > -1:  # считываем все категории
        html = html[html.find('category text="') + 15:]
        if html.find('>') < html.find('/>'):  # если у категории есть подкатегории
            categorys_of_podcast += html[: html.find('"')] + ', '
            subcategorys_of_field = html[html.find('>') + 1: html.find('</itunes:category>')]
            while subcategorys_of_field.find('category text="') > -1:
                subcategorys_of_podcast += '#' + subcategorys_of_field[subcategorys_of_field.find('category text="') + 15: subcategorys_of_field.rfind('"')]
                subcategorys_of_field = subcategorys_of_field[subcategorys_of_field.find('/>') + 2:]
            html = html[html.find('</itunes:category>') + 18:]  # срезаем подкатегории
        else:
            categorys_of_podcast += html[: html.find('"')] + ', '
    if categorys_of_podcast:
        categorys_of_podcast = check_on_shit(categorys_of_podcast)
        if subcategorys_of_podcast:
            subcategorys_of_podcast = check_on_shit(subcategorys_of_podcast)

    print('Название: ' + title_of_podcast + '\n',
          'Описание: ' + description_of_podcast + '\n',
          'Картинка: ' + image_of_podcasts + '\n',
          'Ключевые слова: ' + keyword_of_podcasts + '\n',
          'Автор: ' + author_of_podcast + '\n',
          'Категории: ' + categorys_of_podcast + '\n',
          'Подкатегории: ' + subcategorys_of_podcast + '\n',)

    # if not {'title_of_podcast': title_of_podcast} in util.execute('SELECT title_of_podcast FROM podcasts'):
    #     util.set_new_podcast(title_of_podcast, description_of_podcast, image_of_podcasts, )

    """
        Далее идем к выпускам подкаста, именуется этот тег в rss как item, и его столько сколько всего выпусков.
        Имеем цикл, который ходит по этим тегам, из каждого тега выкачиваем ввсё что в нём есть.
    """

    html = html[html.find('<item>'):]   # так как информация о подкасте уже собрана, обрезаем её и начинаем собирать инфу о выпусках

    while html.find('<item>') > -1:    # до тех пор пока находим новый выпуск

        # получаем блок с этим itemом, чтоб работать не по всей странице
        item_code = html[html.find('<item>') + 7: html.find('</item>')]

        # получаем название выпуска
        title_of_item = item_code[item_code.find('<title>') + 7: item_code.find('</title>')]
        title_of_item = check_on_shit(title_of_item)

        # получаем описание выпуска
        description_of_item = item_code[item_code.find('<description>') + 13: item_code.find('</description>')]
        description_of_item = check_on_shit(description_of_item)

        # переходим в тег с ссылкой на аудио
        enclosure = item_code[item_code.find('<enclosure'):]
        enclosure = enclosure[enclosure.find('url="') + 5:enclosure.find('/>')]
        mp3 = enclosure[: enclosure.find('"')]    # получаем аудио

        # получаем дату публикации выпуска
        pubdata_of_item = item_code[item_code.find('<pubDate>') + 9: item_code.find('</pubDate>')]

        # получаем область с длительностью аудио
        duration_of_item = str()
        if item_code.find('duration') > -1:
            temp_code = item_code[item_code.find('duration>') + 9: item_code.find('duration>') + 20]
            duration_of_item = temp_code[:temp_code.find('</')]    # получаем длительность аудио
            if duration_of_item.find(':') == -1:     # проверяем разделено ли время : (иначе оно указано в секундах)
                duration_of_item = convert_of_time(int(duration_of_item))

        # получаем картинку выпуска если такова есть
        image_of_item = str()
        if item_code.find('image') > -1:
            temp_code = item_code[item_code.find('image') + 5:]
            temp_code = temp_code[temp_code.find('href="') + 6:]
            image_of_item = temp_code[: temp_code.find('"')]

        html = html[html.find('</item>') + 7:]   # режем ту строку с которой отработали, и идем далее
        print('Название выпуска: ' + title_of_item + '\n',
              'Описание выпуска: ' + description_of_item + '\n',
              'Музыка: ' + mp3 + '\n',
              'Дата публикации выпуска: ' + pubdata_of_item + '\n',
              'Длительность выпуска: ' + duration_of_item + '\n',
              'Картинка выпуска: ' + image_of_item + '\n')


if __name__ == '__main__':
    # parse('https://feeds.simplecast.com/CPNlXNwD')
    # parse('https://rss.simplecast.com/podcasts/4464/rss')
    # parse('https://podster.fm/rss.xml?pid=20066')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:516686697/sounds.rss')
    # parse('https://podster.fm/rss.xml?pid=29605')
    # parse('https://meduza.io/rss/podcasts/peremotka')
    # parse('https://mojomedia.ru/feed-podcasts/rebyata-my-potrahalis')
    # parse('http://feeds.feedburner.com/bizipodcast')
    # parse('https://anchor.fm/s/84ed588/podcast/rss')
    # parse('https://podster.fm/rss.xml?pid=40940')
    # parse('http://sharkov.podfm.ru/rss/rss.xml')
    # parse('https://feeds.fireside.fm/batinakonsol/rss')
    # parse('https://web-standards.ru/podcast/feed/')
    # parse('https://feeds.simplecast.com/hbz_rFz4')
    # parse('https://mojomedia.ru/feed-podcasts/dikie-utki')
    # parse('http://feeds.feedburner.com/DariaSadovaya')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:328939120/sounds.rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:132344904/sounds.rss')
    # parse('http://feeds.feedburner.com/pod24fps')
    # parse('https://anchor.fm/s/6f169f8/podcast/rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:679508342/sounds.rss')
    parse('http://feeds.feedburner.com/americhka/oBlg')