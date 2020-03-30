#!/home/tgpodcast/venv/bin/python
import multiprocessing
import re
import time
from datetime import datetime
from datetime import timedelta
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
        if not each_podcast.get('url_podcast').startswith('http'):  # если нет http / https - на помойку
            util.add_url_in_error_links(each_podcast.get('id'), each_podcast.get('url_podcast'),
                                        reason='Ссылка без http/https')
            continue
        try:
            while threading.active_count() > 25:
                print('Sleep 1 sec')
                time.sleep(1)
            else:
                print('id url: ', each_podcast['id'])
                if not util.exist_channel(each_podcast.get('id')):
                    print('start url:   ', each_podcast.get('url_podcast'))
                    # threading.Thread(target=parse, args=(each_podcast.get('url_podcast'), each_podcast.get('id'))).start()  # ебашим всё в потоки
                    parse(each_podcast.get('url_podcast'), each_podcast.get('id'))   # парсим по одному без потоков
                else:
                    util.change_status(each_podcast.get('url_podcast'), 2, each_podcast.get('id'))

        except requests.exceptions.ConnectionError:
            util.add_url_in_error_links(id_podcast=each_podcast.get('id'), url=each_podcast.get('url_podcast'), reason="Нет коннекта к url")


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
    if each_podcast.startswith('valid URL'):  # если юрл / рсс поломанные
        util.add_url_in_error_links(id_podcasts, old_url, reason='Не валидный юрл / рсс')
        return
    elif each_podcast.startswith('unes error:'):
        util.add_url_in_error_links(id_podcasts, old_url, reason='Не доступен в стор в какой-то стране')
        return
    else:  # если всё нормально, то есть была ссылка на айтунс, стала на рсс
        if each_podcast.startswith('L appears to ') is True:  # если ссылька не изменена
            each_podcast = old_url
    try:
        # ЭТО ДЛЯ ТОГО, чтоб узнать не бракованный ли урл на время загрузки...
        start = datetime.now()
        Thread = multiprocessing.Process(target=requests.get, args=(each_podcast,))
        Thread.start()
        while Thread.is_alive() and datetime.now() - start < timedelta(seconds=60):
            time.sleep(1)
            print('sleep')
        else:
            if Thread.is_alive():
                Thread.close()
                util.add_url_in_error_links(id_podcasts, old_url, reason='Infinity load')
                return

        if requests.get(each_podcast).status_code != 200:
            raise requests.exceptions.ConnectionError
        try:
            html = requests.get(each_podcast).content.decode('utf-8')  # получаем саму ленту
        except Exception as e:
            print(e)
            util.add_url_in_error_links(id_podcasts, old_url, reason='Unconnect closed port 443')

    except UnicodeDecodeError:
        html = requests.get(each_podcast).text
    except requests.exceptions.MissingSchema:
        print('ERROR PARSE -- ' + old_url)
        util.add_url_in_error_links(id_podcasts, old_url, reason='Cant connected on rss')
        return
    except requests.exceptions.SSLError:  # если сайт плохой (заразный тип)
        try:
            html = requests.get(each_podcast, verify=False).text
        except Exception as e:
            print(e)
            util.add_url_in_error_links(id_podcasts, old_url, reason='SSL error')
            return
    except requests.exceptions.ConnectionError:
        util.add_url_in_error_links(id_podcasts, old_url, reason='Error (404 or 503)')
        return
    except requests.exceptions.InvalidSchema:  # если нет доступа по какой-то причине, в основном из-за страны
        print('Нет коннекта - ', old_url)
        util.add_url_in_error_links(id_podcasts, old_url, reason='No access to iTunes from Russia')
        return
    except Exception as e:  # если нет доступа по какой-то причине, в основном из-за страны
        print('Неизвестная ошибка', e)
        util.add_url_in_error_links(id_podcasts, old_url, reason='Unknown error')
        return

    if html[:html.find('<item>')].find('feeds.feedburner') > -1 or len(re.findall(r'<script[^>]*', html)) > 2 or each_podcast.startswith('unes error'):
        util.add_url_in_error_links(id_podcasts, each_podcast, reason='Bad rss')
        return

    # заносим в бд изменение (если ссылки не изменны, то меняем только статус) + если с урлом что-то не так не продолжаем его парсить
    if util.change_url(id_podcasts, each_podcast, 2) is False:
        return

    if html.find(' >') > -1:
        for tag in re.findall(r'<.*\s>', html):
            try:
                html = re.sub(tag, tag[:-2] + tag[-1], html)
            except:
                continue

    pre_item_html = html[:html.find('<item>')]  # записываем в ленте часть перед выпусками (для быстродействия?)

    # находим название подкаста
    pre_title = re.search(r'<title.*>.*</title>', pre_item_html)
    title_podcast = str()
    if pre_title:  # если тайтл есть, но рсска пока норм, иначе в помойку
        title_podcast = pre_title.group()
        title_podcast = title_podcast[title_podcast.find('>') + 1:title_podcast.find('</')]
        title_podcast = func_for_clear_text.check_on_shit(title_podcast)  # название пригодится при парсинге выпусков
        if len(title_podcast) > 120:
            title_podcast = str()
    else:
        util.add_url_in_error_links(id_podcasts, old_url, reason='Некорректная рсс лента.')

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
    if pre_item_html.find('keywords>') > -1:  # если есть ключевые слова
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

    util.set_new_podcast(id_podcasts, title_podcast, description_podcast, categorys_podcast,
                         image_podcasts, author_podcast, subcategorys_podcast, keyword_podcasts)


if __name__ == '__main__':
    pre_parse()
