import re
import requests
import util


def check_on_shit(string):      # чистим полученные строки от говна, типа сидата или спецсимволы хтмл
    if string.find('&') > -1:
        string = encode_from_html(string)
    if string.find('<![CDATA[') > -1:   # чистим строку от cdata
        string = string[string.find('<![CDATA[') + 9: string.find(']]>')]
    if string.find('&lt') > -1:
        string = clear_from_decor(string)
    string = clear_from_tags(string)
    return string


def encode_from_html(string):   # перекодировка из html символов в обычные
    while re.search(r'&#\d{1,4};', string) is not None:     # чистим от цифр, заменяя буквами если вохможно (&#1044;)
        swap_word = re.search(r'&#\d{1,4};', string)[0]    # копируем изменяемое слово
        if len(swap_word) != 7 or not 1040 <= int(swap_word[-5:-1]) <= 1103:  # все слова которые не буквы, меняем на пробел
            new_word = ' '
        else:
            new_word = chr(int(re.search(swap_word, string)[0][-5:-1]))
        string = re.sub(swap_word, new_word, string)

    while re.search(r'&\w{1,8};', string) is not None:  # чистим от кода на буквах (&amp;)
        string = re.sub(re.search(r'&\w{1,8};', string)[0], '', string)
    return string


def clear_from_decor(string):   # чистим от плохой рссленты (c декором которая)
    while string.startswith('&lt;'):    # чистим от тега lt(он обычно всё инициирует, таблицы, картинки)
        string = string[string.find('&gt;') + 4:]
    while string.find('&lt;') > -1:     # опять таки чистим от него же но уже не в начале текста
        string = string[:string.find('&lt;')] + '\n' + string[string.find('&gt;') + 4:]
    return string


def clear_from_tags(string):
    if string.find('<p>') > -1:
        string = string.replace('<p>', '')
        string = string.replace('</p>', '')
    if string.find('<br />') > -1:
        string = string.replace('<br />', '')
    if string.find('<a href="') > -1:
        string = string[:string.find('<a href="')] + string[string.find('">') + 3:] + ' '
    if string.find('<strong>') > -1:
        string = string.replace('<strong>', '')

    return string


def convert_of_time(time):      # конвертация времени из секунд в часы
    return str(time // 3600) + ':' + str(time // 60 % 60) + ':' + str(time % 60)


def parse_category(html):   # парсим категории
    categorys, subcategorys = str(), str()
    while html.find('category ') > -1:  # считываем все категории
        html = html[html.find('category text="') + 15:]
        if html.find('>') < html.find('/>'):  # если у категории есть подкатегории
            categorys += html[: html.find('"')] + ', '
            subcategorys_of_field = html[html.find('>') + 1: html.find('</itunes:category>')]
            while subcategorys_of_field.find('category text="') > -1:
                subcategorys += subcategorys_of_field[subcategorys_of_field.find('category text="') + 15: subcategorys_of_field.rfind('"')]  + ', '
                subcategorys_of_field = subcategorys_of_field[subcategorys_of_field.find('/>') + 2:]
            html = html[html.find('</itunes:category>') + 18:]  # срезаем подкатегории
        else:
            categorys += html[: html.find('"')] + ', '
    if categorys:
        categorys = check_on_shit(categorys)
        if subcategorys:
            subcategorys = check_on_shit(subcategorys)
    return categorys.split(', '), subcategorys.split(', ')


def parse_keywords(html):
    temp_html = html[html.find('keywords>') + 9:]  # временная срезка, для нахождения ключ. слов
    return check_on_shit(temp_html[: temp_html.find('</')]).replace(' ', '').split(',')


def parse_description(html):
    temp_code = html[html.find('description>') + 12:]
    return check_on_shit(temp_code[: temp_code.find('</')])


def clear_pubdata(string):
    dict_of_day = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                   'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    if string[1] == ' ':    # для нормального времени (2 -> 02)
        string = '0' + string[0] + ' ' + string[2:]
    month = re.search(r'\w\w\w', string)[0]
    string = re.sub(month, dict_of_day.get(month), string)  # запуливаем вместо названия месяца номер месяца
    string = re.sub(r'[ :]', '', string)    # вместо пробела и двоиточия ничего, в инт бахаем
    return string[4:8] + string[2:4] + string[:2] + string[-6:]   # подводим под шаблон бд


def word_with_time(string):
    string = string.replace(':', '')
    if len(string) == 4 and int(string) > 5959:




def parse():
    """
            Берем с бд все ссылки на подкасты, проходимся по ним, если у подкаста метка 0, то не качаем его инфу,
        а сразу переходим к выпускам, иначе, качаем и инфу.

    """
    # html = requests.get(url).content.decode('utf-8')
    for each_podcast in util.check_new_podcast():   # проходимся по ВСЕМ подкастам
        html = requests.get(each_podcast.get('url_of_podcast')).content.decode('utf-8')
        pre_item_html = html[:html.find('<item>')]
        # находим название подкаста
        title_of_podcast = pre_item_html[pre_item_html.find('<title>') + 7: pre_item_html.find('</title>')]
        title_of_podcast = check_on_shit(title_of_podcast)  # название пригодится при парсинге выпуском

        if each_podcast.get('download') == 1:# под этим таб
            # находим описание подкаста
            description_of_podcast = parse_description(pre_item_html)

            # находим картинку подкаста
            if pre_item_html.find('<image>') > -1:
                image_of_podcasts = pre_item_html[pre_item_html.find('<image>') + 7: pre_item_html.find('</image>')]
                image_of_podcasts = image_of_podcasts[image_of_podcasts.find('<url>') + 5: image_of_podcasts.find('</url>')]
            else:
                image_of_podcasts = pre_item_html[pre_item_html.find('image') + 5:]
                image_of_podcasts = image_of_podcasts[image_of_podcasts.find('href="') + 6:]
                image_of_podcasts = image_of_podcasts[: image_of_podcasts.find('"')]

            # находим ключевые слова если они есть
            keyword_of_podcasts = str()
            if pre_item_html.find('keywords>') > -1:     # если есть ключевые слова
                keyword_of_podcasts = parse_keywords(pre_item_html)

            # находим автора, если он есть
            author_of_podcast = str()
            if pre_item_html.find('author>') > -1:
                temp_code = pre_item_html[pre_item_html.find('author>') + 7:]
                author_of_podcast = check_on_shit(temp_code[:temp_code.find('</')])

            # находим категории если они есть
            categorys_of_podcast, subcategorys_of_podcast = parse_category(pre_item_html)

            # print('Название: ' + title_of_podcast + '\n',
            #       'Описание: ' + description_of_podcast + '\n',
            #       'Картинка: ' + image_of_podcasts + '\n',
            #       'Ключевые слова: ' , keyword_of_podcasts , '\n',
            #       'Автор: ' + author_of_podcast + '\n',
            #       'Категории: ' , categorys_of_podcast , '\n',
            #       'Подкатегории: ' , subcategorys_of_podcast , '\n',
            #       )

            util.set_new_podcast(each_podcast.get('url_of_podcast'), title_of_podcast, description_of_podcast, categorys_of_podcast,
                                 image_of_podcasts, author_of_podcast, subcategorys_of_podcast, keyword_of_podcasts)

        """
            Далее идем к выпускам подкаста, именуется этот тег(в плане сам выпуск) в rss как item, 
            и его столько сколько всего выпусков.
            Имеем цикл, который ходит по этим тегам, из каждого тега выкачиваем ввсё что в нём есть.
        """

        html = html[html.find('<item>'):]   # обрезаем весь html до item

        while html.find('<item>') > -1:    # до тех пор пока находим новый выпуск

            # получаем блок с этим itemом, чтоб работать не по всей странице
            item_code = html[html.find('<item>') + 7: html.find('</item>')]

            # получаем название выпуска
            title_of_item = item_code[item_code.find('<title>') + 7: item_code.find('</title>')]
            title_of_item = check_on_shit(title_of_item)

            # if util.check_item(title_of_item, title_of_podcast):    # если такой выпуск уже есть, выходим
            #     print('sex')
            #     return

            # получаем описание выпуска
            description_of_item = parse_description(item_code)

            # переходим в тег с ссылкой на аудио
            enclosure = item_code[item_code.find('<enclosure'):]
            enclosure = enclosure[enclosure.find('url="') + 5:enclosure.find('/>')]
            mp3 = enclosure[: enclosure.find('"')]    # получаем аудио

            # получаем дату публикации выпуска
            pubdata_of_item = clear_pubdata(item_code[item_code.find('<pubDate>') + 14: item_code.find('</pubDate>') - 6])

            # получаем область с длительностью аудио
            duration_of_item = str()
            if item_code.find('duration>') > -1:
                temp_code = item_code[item_code.find('duration>') + 9: item_code.find('duration>') + 20]
                duration_of_item = temp_code[:temp_code.find('</')]    # получаем длительность аудио
                if duration_of_item and duration_of_item.find(':') == -1:     # проверяем разделено ли время : (иначе оно указано в секундах)
                    duration_of_item = convert_of_time(int(duration_of_item))
                duration_of_item = work_with_time(duration_of_item)

            # получаем картинку выпуска если такова есть
            image_of_item = str()
            if item_code.find('image ') > -1 and item_code.find('"image"') == -1:
                temp_code = item_code[item_code.find('image ') + 6:]
                temp_code = temp_code[temp_code.find('href="') + 6:]
                image_of_item = temp_code[: temp_code.find('"')]

            categorys_of_item, subcategorys_of_item = parse_category(item_code[:item_code.find('</item>')])

            # находим ключевые слова если они есть
            keyword_of_item = str()
            if item_code.find('keywords>') > -1:  # если есть ключевые слова
                keyword_of_item = parse_keywords(item_code[:item_code.find('</item>')])

            util.set_new_item(title_of_podcast, title_of_item, description_of_item, mp3, image_of_item,
                              pubdata_of_item, duration_of_item, categorys_of_item, subcategorys_of_item, keyword_of_item)
            html = html[html.find('</item>') + 7:]   # режем ту строку с которой отработали, и идем далее
            # print('Название выпуска: ' + title_of_item + '\n',
            #       'Описание выпуска: ' + description_of_item + '\n',
            #       'Музыка: ' + mp3 + '\n',
            #       'Дата публикации выпуска: ' + pubdata_of_item + '\n',
            #       'Длительность выпуска: ' + duration_of_item + '\n',
            #       'Картинка выпуска: ' + image_of_item + '\n',
            #       'Категории выпуска: ', categorys_of_item , '\n',
            #       'Подкатегории выпуска: ', subcategorys_of_item , '\n',
            #       'Ключевые слова выпуска: ', keyword_of_item , '\n',
            #       )


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
    # parse('http://feeds.feedburner.com/americhka/oBlg')
    # parse('https://feeds.simplecast.com/TicU3npd')
    # parse('https://podster.fm/rss.xml?pid=42935')
    # parse('https://podster.fm/rss.xml?pid=62505')
    # parse('http://basicblockradio.libsyn.com/rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:542232678/sounds.rss')
    # parse('https://aerostatica.ru/podcast.xml')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:516686697/sounds.rss')
    # parse('https://feeds.simplecast.com/d1D4qHVy')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:569213187/sounds.rss')
    # parse('http://toinfinityandbeyond.libsyn.com/rss')
    # parse('https://warispeace.podigee.io/feed/mp3')
    # parse('http://feeds.feedburner.com/kommentator_podcast')
    # parse('https://echo.msk.ru/programs/garage/rss-audio.xml')
    # parse('https://pogovorim.stellav.ru/feed/podcast/')
    # parse('https://feeds.simplecast.com/o2q3_tiT')
    # parse('https://meduza.io/rss/podcasts/delo-sluchaya')
    # parse('https://anchor.fm/s/d6b7490/podcast/rss')
    # parse('https://podster.fm/rss.xml?pid=69579')
    # parse('https://pinecast.com/feed/designer')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:436210245/sounds.rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:602278230/sounds.rss')
    # parse('https://podster.fm/rss.xml?pid=35648')
    # parse('https://feeds.simplecast.com/v1cJ8X2Z')
    parse()
    pass
