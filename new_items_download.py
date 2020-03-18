#!/home/tgpodcast/venv/bin/python
import re
import time
import func_for_clear_text
import threading
import requests
import util


def pre_parse():
    """
        Фукнкция которая парсит все url'ы с бд, и под каждый url выделяет поток, после чего парсит
        с url'a инфу.
    """
    for each_podcast in util.get_podcast_url(3):  # проходимся по подкастам c id 1
        try:
            while threading.active_count() > 30:
                print('Sleep 1 sec')
                time.sleep(1)
            else:
                print('id url: ', each_podcast['id'])

                if not util.exist_channel(each_podcast.get('id')):
                    print('start url:   ', each_podcast.get('url_podcast'))
                    threading.Thread(target=parse, args=(
                    each_podcast.get('url_podcast'), each_podcast.get('id'))).start()  # ебашим всё в потоки
                # parse(each_podcast.get('url_podcast'))   # парсим по одному без потоков
        except requests.exceptions.ConnectionError:
            util.add_url_in_error_links(each_podcast.get('url_podcast'))


def parse(each_podcast, id_podcasts):
    """
        Качаем только новые выпуски (в цикле по кд проверка на новину выпуска,
        если не новый то кик с цыкла)
    """
    try:
        if requests.get(each_podcast).status_code != 200:
            raise requests.exceptions.ConnectionError
        html = requests.get(each_podcast).content.decode('utf-8')  # получаем саму ленту
    except UnicodeDecodeError:
        html = requests.get(each_podcast).text
    except requests.exceptions.MissingSchema:
        print('ERROR PARSE -- ' + each_podcast)
        util.add_url_in_error_links(id_podcasts, each_podcast, reason='Ошибка из-за того что нет коннекта к рсс.')
        return
    except requests.exceptions.SSLError:  # если сайт плохой (заразный тип)
        html = requests.get(each_podcast, verify=False).text
    except requests.exceptions.ConnectionError:
        util.add_url_in_error_links(id_podcasts, each_podcast, reason='Ошибка коннекта к сайту(404 или 503)')
        return
    except requests.exceptions.InvalidSchema:  # если нет доступа по какой-то причине, в основном из-за страны
        print('Нет коннекта - ', each_podcast)
        util.add_url_in_error_links(id_podcasts, each_podcast, reason='Нет доступа по причине, страны или чего-то подобного')
        return

    if html.find(' >') > -1:
        for tag in re.findall(r'<.*\s>', html):
            try:
                html = re.sub(tag, tag[:-2] + tag[-1], html)
            except:
                continue

    html = html[html.find('<item>'):]   # обрезаем весь html до item
    list_of_items = list()

    while html.find('<item>') > -1:    # до тех пор пока находим новый выпуск
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

        if util.check_item(id_podcasts, mp3):    # если такой выпуск уже есть, не выходим, а просто его пропускаем
            html = html[html.find('</item>') + 7:]  # режем ту строку с которой отработали, и идем далее
            break

        # получаем описание выпуска
        description_item = None
        if item_code.find('description') > -1:
            description_item = func_for_clear_text.parse_description(item_code)

        # получаем дату публикации выпуска
        pubdata_item = func_for_clear_text.clear_pubdata(
            item_code[item_code.find('<pubDate>') + 14: item_code.find('</pubDate>') - 6])

        # получаем область с длительностью аудио
        duration_item = str()
        duration_code = re.search(r'duration[^>]*>', item_code)  # для обхода плохо написанного тега
        if duration_code:
            temp_code = item_code[item_code.find(duration_code.group()) + len(duration_code.group()):]
            duration_item = temp_code[:temp_code.find('</')]  # получаем длительность аудио
            if duration_item.startswith('<![CDATA'):
                duration_item = duration_item[9:-3]
            if duration_item and duration_item.isdigit() and duration_item.find(
                    ':') == -1:  # проверяем разделено ли время : (иначе оно указано в секундах)
                duration_item = func_for_clear_text.convert_time(int(duration_item))

        # получаем картинку выпуска если такова есть
        image_item = str()
        if item_code.find('image ') > -1 and item_code.find('"image"') == -1:
            temp_code = item_code[item_code.find('image ') + 6:]
            temp_code = re.search(r'href=[^\"\']*(\"|\')[^\"|\']*', temp_code)
            if temp_code:
                temp_code = temp_code.group()
                image_item = temp_code[temp_code.find(re.search(r'\"|\'', temp_code).group()) + 1:]
            else:
                image_item = str()

        # categorys_item, subcategorys_item = func_for_clear_text.parse_category(item_code[:item_code.find('</item>')])

        # находим ключевые слова если они есть
        keyword_item = str()
        if item_code.find('keywords>') > -1:  # если есть ключевые слова
            keyword_item = func_for_clear_text.parse_keywords(item_code[:item_code.find('</item>')])

        # util.set_new_item(title_podcast, title_item, description_item, mp3, image_item,
        #                   pubdata_item, duration_item, categorys_item, subcategorys_item, keyword_item)

        list_of_items.append((title_item, description_item, mp3, image_item,
                              pubdata_item, duration_item, keyword_item))
        html = html[html.find('</item>') + 7:]  # режем ту строку с которой отработали, и идем далее
        print('Название выпуска: ' + title_item + '\n')

    util.set_new_item(id_podcasts, list_of_items)


if __name__ == '__main__':
    pre_parse()
