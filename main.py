import re
import requests
import util


def encode_from_html(string):   # перекодировка из html символов в обычные
    while re.search(r'&#\d{1,4};', string) is not None:
        swap_word = re.search(r'&#\d{1,4};', string)[0]    # копируем изменяемое слово
        if len(swap_word) != 7 or not 1040 <= int(swap_word[-5:-1]) <= 1103:  # все слова которые не буквы, меняем на пробел
            new_word = ' '
        else:
            new_word = chr(int(re.search(swap_word, string)[0][-5:-1]))
        string = re.sub(swap_word, new_word, string)
    return string


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
    if html.find('keywords>') > -1:     # если есть ключевые слова
        temp_html = html[html.find('keywords>') + 9:]   # временная срезка, для нахождения ключ. слов
        keyword_of_podcasts += temp_html[: temp_html.find('</')]
        if keyword_of_podcasts.find('#') > -1:
            keyword_of_podcasts = encode_from_html(keyword_of_podcasts)

    # находим категории если они есть
    categorys_of_podcast = str()
    mark = False    # флажок на подкатегорию
    while html.find('category text="') > -1:  # считываем все категории
        html = html[html.find('category text="') + 15:]
        categorys_of_podcast += html[: html.find('"')] + ', '
        html = html[html.find('>') + 1:]

    print(title_of_podcast, description_of_podcast, image_of_podcasts, keyword_of_podcasts, categorys_of_podcast)

    # if not {'title_of_podcast': title_of_podcast} in util.execute('SELECT title_of_podcast FROM podcasts'):
    #     util.set_new_podcast(title_of_podcast, description_of_podcast, image_of_podcasts, )

    """
        Далее идем к выпускам подкаста, именуется этот тег в rss как item, и его столько сколько всего выпусков.
        Имеем цикл, который ходит по этим тегам, из каждого тега выкачиваем ввсё что в нём есть.
    """

    html = html[html.find('<item>'):]   # так как информация о подкасте уже собрана, обрезаем её и начинаем собирать инфу о выпусках

    ls_of_items = []    # впредь выпуски будут items, это список со всеми выпусками
    while html.find('<item>') > -1:    # до тех пор пока находим новый выпуск

        # получаем блок с этим itemом, чтоб работать не по всей странице
        item_code = html[html.find('<item>') + 7: html.find('</item>')]

        # получаем название выпуска
        title_of_item = item_code[item_code.find('<title>') + 7: item_code.find('</title>')]

        # получаем описание выпуска
        description_of_item = item_code[item_code.find('<description>') + 13: item_code.find('</description>')]
        if description_of_item.find('<![CDATA[') > -1:
            description_of_item = description_of_item[
                                     description_of_item.find('<![CDATA[') + 9: description_of_item.find(']]>')]

        # переходим в тег с ссылкой на аудио
        enclosure = item_code[item_code.find('<enclosure'):]
        mp3 = enclosure[enclosure.find('url="') + 5: enclosure.find('mp3') + 3]    # получаем аудио

        # получаем дату публикации выпуска
        pubdata_of_item = item_code[item_code.find('<pubDate>') + 9: item_code.find('</pubDate>')]

        # получаем область с длительностью аудио
        temp_code = item_code[item_code.find('duration>') + 9: item_code.find('duration>') + 20]
        duration_of_item = temp_code[:temp_code.find('</')]    # получаем длительность аудио

        # получаем область с картинкой выпуска
        temp_code = item_code[item_code.find('image ') + 6:]
        image_of_item = temp_code[temp_code.find('"') + 1: temp_code.find('"/>')]

        html = html[html.find('</item>') + 7:]   # режем ту строку с которой отработали, и идем далее
        print(encode_from_html(title_of_item), '\n', description_of_item, '\n', mp3, '\n',
              pubdata_of_item, '\n', duration_of_item, '\n', image_of_item)


if __name__ == '__main__':
    parse('https://feeds.simplecast.com/CPNlXNwD')
    # parse('https://podster.fm/rss.xml?pid=20066')
    # parse('https://podster.fm/rss.xml?pid=29605')
    # parse('https://meduza.io/rss/podcasts/peremotka')
    # parse('https://mojomedia.ru/feed-podcasts/rebyata-my-potrahalis')
