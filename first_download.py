#!/home/tgpodcast/venv/bin/python
import re
import time
from datetime import datetime

import func_for_clear_text
import threading
import requests
import util


def pre_parse():
    """
        Фукнкция которая парсит все url'ы с бд, и под каждый url выделяет поток, после чего парсит
        с url'a инфу.
    """
    for each_podcast in util.get_podcast_url(1):  # проходимся по подкастам c id 1
        if not each_podcast.get('url_podcast').startswith('http'):   # если нет http / https - на помойку
            util.add_url_in_error_links(each_podcast.get('url_podcast'), reason='Ссылка без http/https')
            continue
        try:
            while threading.active_count() > 50:
                print('Sleep 1 sec')
                time.sleep(1)
            else:
                print('id url: ', each_podcast['id'])

                if not util.exist_channel(each_podcast.get('id')):
                    print('start url:   ', each_podcast.get('url_podcast'))
                    threading.Thread(target=parse, args=(each_podcast.get('url_podcast'), each_podcast['id'])).start()  # ебашим всё в потоки
                # parse(each_podcast.get('url_podcast'))   # парсим по одному без потоков
        except requests.exceptions.ConnectionError:
            util.add_url_in_error_links(each_podcast.get('url_podcast'))


def parse(each_podcast, id_podcasts):
    """
            Вначале закачиваю инфу о подкасте, название, и прочее;
        После благодаря циклу парсим выпуски, если что кол-во выпусков задано на
        22-ой строке.
            После завершения парсинга первых n выпусков, даем подкасту статус 2, который
        оповещает о том, что данный подккаст требует дозагрузки ВСЕХ подкастов.
    """

    old_url = each_podcast
    each_podcast = requests.get('http://picklemonkey.net/flipper/extractor.php?feed='
                                + each_podcast).text[12:-2].replace('\/', '/')
    if each_podcast.startswith('valid URL'):    # если юрл / рсс поломанные
        util.add_url_in_error_links(old_url, reason='Не валидный юрл / рсс')
        return
    elif each_podcast.startswith('L appears to ') is False:     # если всё норм с РСС лентой (если изначально её ввели)
        util.change_url(each_podcast, old_url)
    else:   # если всё нормально, то есть была ссылка на айтунс, стала на рсс
        each_podcast = old_url
    try:
        html = requests.get(each_podcast).content.decode('utf-8')     # получаем саму ленту
    except UnicodeDecodeError:
        html = requests.get(each_podcast).text
    except requests.exceptions.MissingSchema:
        print('ERROR PARSE -- ' + each_podcast)
        util.add_url_in_error_links(old_url, reason='Ошибка из-за того что нет коннекта к рсс.')
        return
    except requests.exceptions.SSLError:    # если сайт плохой (заразный тип)
        html = requests.get(each_podcast, verify=False).text
    except requests.exceptions.InvalidSchema:   # если нет доступа по какой-то причине, в основном из-за страны
        print('Нет коннекта - ', old_url)
        util.add_url_in_error_links(old_url, reason='Нет доступа по причине, страны или чего-то подобного')
        return

    if html.find('feeds.feedburner') > -1 or re.search(r'<script[^>]*', html) or each_podcast.startswith('unes error'):
        util.add_url_in_error_links(each_podcast, reason='Плохая рсс лента (с рекламой или скриптами и прочим)')
        return

    # util.change_url(old_url, each_podcast, 2)

    if html.find(' >') > -1:
        for tag in re.findall(r'<.*\s>', html):
            try:
                html = re.sub(tag, tag[:-2] + tag[-1], html)
            except:
                continue

    pre_item_html = html[:html.find('<item>')]      # записываем в ленте часть перед выпусками (для быстродействия?)

    # находим название подкаста
    pre_title = re.search(r'<title[^>]*>[^<]*</title>', pre_item_html)
    title_podcast = str()
    if pre_title:   # если тайтл есть, но рсска пока норм, иначе в помойку
        title_podcast = pre_title.group()
        title_podcast = title_podcast[title_podcast.find('>') + 1:title_podcast.rfind('</')]
        title_podcast = func_for_clear_text.check_on_shit(title_podcast)  # название пригодится при парсинге выпусков
    else:
        util.add_url_in_error_links(old_url, reason='Некорректная рсс лента.')

    # находим описание подкаста
    description_podcast = None
    if pre_item_html.find('description') > -1:
        description_podcast = func_for_clear_text.parse_description(pre_item_html)

    image_podcasts = str()
    # находим картинку подкаста
    if pre_item_html.find('<image>') > -1:
        image_podcasts = pre_item_html[pre_item_html.find('<image>') + 7: pre_item_html.find('</image>')]
        image_podcasts = image_podcasts[image_podcasts.find('<url>') + 5: image_podcasts.find('</url>')]
    elif pre_item_html.find('image') > -1:
        image_podcasts = pre_item_html[pre_item_html.find('image') + 5:]
        image_podcasts = image_podcasts[image_podcasts.find('href="') + 6:]
        image_podcasts = image_podcasts[: image_podcasts.find('"')]

    # находим ключевые слова если они есть
    keyword_podcasts = str()
    if pre_item_html.find('keywords>') > -1:     # если есть ключевые слова
        keyword_podcasts = func_for_clear_text.parse_keywords(pre_item_html)

    # находим автора, если он есть
    author_podcast = str()
    if pre_item_html.find('author>') > -1:
        temp_code = pre_item_html[pre_item_html.find('author>') + 7:]
        author_podcast = func_for_clear_text.check_on_shit(temp_code[:temp_code.find('</')])

    # находим категории если они есть
    categorys_podcast, subcategorys_podcast = func_for_clear_text.parse_category(pre_item_html)

    print('##############################################################')
    print('Link ', each_podcast)
    print('Name chanel: ' + title_podcast + '\n')
    
    util.set_new_podcast(id_podcasts, each_podcast, title_podcast, description_podcast, categorys_podcast,
                         image_podcasts, author_podcast, subcategorys_podcast, keyword_podcasts)

    """
        Далее идем к выпускам подкаста, именуется этот тег(в плане сам выпуск) в rss как item, 
        и его столько сколько всего выпусков.
        Имеем цикл, который ходит по этим тегам, из каждого тега выкачиваем ввсё что в нём есть.
    """

    html = html[html.find('<item>'):]   # обрезаем весь html до item
    amount_item = 0  # кол-во выпусков, качаем не более 50
    list_of_items = list()
    while html.find('<item>') > -1 and amount_item < 50:    # до тех пор пока находим новый выпуск
        amount_item += 1
        # получаем блок с этим itemом, чтоб работать не по всей странице
        item_code = html[html.find('<item>') + 7: html.find('</item>')]

        # получаем название выпуска
        title_item = item_code[item_code.find('<title>') + 7: item_code.find('</title>')]
        title_item = func_for_clear_text.check_on_shit(title_item)

        # переходим в тег с ссылкой на аудио
        mp3 = str()
        if item_code.find('<enclosure') > -1:
            enclosure = item_code[item_code.find('<enclosure'):]
            enclosure = enclosure[enclosure.find('url'):enclosure.find('>')]
            mp3 = re.search(r'url=[^\'\"]*(\'|\")[^\'\"]*', enclosure, flags=re.DOTALL).group()
            mp3 = mp3[mp3.find(re.search(r'\"|\'', mp3).group()) + 1:]  # получаем аудио

        # получаем описание выпуска
        description_item = None
        if item_code.find('description') > -1:
            description_item = func_for_clear_text.parse_description(item_code)

        # получаем дату публикации выпуска
        pubdata_item = func_for_clear_text.clear_pubdata(item_code[item_code.find('<pubDate>') + 14: item_code.find('</pubDate>') - 6])

        # получаем область с длительностью аудио
        duration_item = str()
        duration_code = re.search(r'duration[^>]*>', item_code)     # для обхода плохо написанного тега
        if duration_code:
            temp_code = item_code[item_code.find(duration_code.group()) + len(duration_code.group()):]
            duration_item = temp_code[:temp_code.find('</')]     # получаем длительность аудио
            if duration_item.startswith('<![CDATA'):
                duration_item = duration_item[9:-3]
            if duration_item and duration_item.isalnum() and duration_item.find(':') == -1:     # проверяем разделено ли время : (иначе оно указано в секундах)
                duration_item = func_for_clear_text.convert_time(int(duration_item))

        # получаем картинку выпуска если такова есть
        image_item = str()
        if item_code.find('image ') > -1 and item_code.find('"image"') == -1:
            temp_code = item_code[item_code.find('image ') + 6:]
            temp_code = re.search(r'href=[^\"\']*(\"|\')[^\"|\']*', temp_code).group()
            image_item = temp_code[temp_code.find(re.search(r'\"|\'', temp_code).group()) + 1:]

        # categorys_item, subcategorys_item = func_for_clear_text.parse_category(item_code[:item_code.find('</item>')])

        # находим ключевые слова если они есть
        keyword_item = str()
        if item_code.find('keywords>') > -1:  # если есть ключевые слова
            keyword_item = func_for_clear_text.parse_keywords(item_code[:item_code.find('</item>')])

        # util.set_new_item(title_podcast, title_item, description_item, mp3, image_item,
        #                   pubdata_item, duration_item, categorys_item, subcategorys_item, keyword_item)

        list_of_items.append((title_item, description_item, mp3, image_item,
                              pubdata_item, duration_item, keyword_item))
        html = html[html.find('</item>') + 7:]   # режем ту строку с которой отработали, и идем далее
        print('Название выпуска: ' + title_item + '\n')

    util.set_new_item(id_podcasts, list_of_items)


if __name__ == '__main__':
    pre_parse()
