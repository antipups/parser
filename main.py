import func_for_clear_text
import threading
import requests
import util


def pre_parse():
    """
        Фукнкция которая парсит все url'ы с бд, и под каждый url выделяет поток, после чего парсит
        с url'a инфу.
    """
    for each_podcast in util.check_new_podcast():  # проходимся по ВСЕМ подкастам
        if each_podcast.get('status_of_podcast') == 1:  # если подкаст не скачан ещё
            threading.Thread(target=parse, args=(each_podcast.get('url_of_podcast'), )).start()   # ебашим всё в потоки
            # parse(each_podcast)   # парсим по одному без потоков


def parse(each_podcast):
    """
            Вначале закачиваю инфу о подкасте, название, и прочее;
        После благодаря циклу парсим выпуски, если что кол-во выпусков задано на
        87-ой строке.
            После завершения парсинга первых n выпусков, даем подкасту статус 2, который
        оповещает о том, что данный подккаст требует дозагрузки ВСЕХ подкастов.
    """
    if each_podcast.find('podcasts.apple.com') > -1:    # если ссылка прям с эпл подкастов а не на рсс
        old_url = each_podcast
        each_podcast = requests.get('http://picklemonkey.net/flipper/extractor.php?feed='
                                    + each_podcast).text[12:-2].replace('\/', '/')
        util.change_of_url(each_podcast, old_url)
    html = requests.get(each_podcast).content.decode('utf-8')     # получаем саму ленту
    pre_item_html = html[:html.find('<item>')]      # записываем в ленте часть перед выпусками (для быстродействия?)

    # находим название подкаста
    title_of_podcast = pre_item_html[pre_item_html.find('<title>') + 7: pre_item_html.find('</title>')]
    title_of_podcast = func_for_clear_text.check_on_shit(title_of_podcast)  # название пригодится при парсинге выпусков

    # находим описание подкаста
    description_of_podcast = None
    if pre_item_html.find('description') > -1:
        description_of_podcast = func_for_clear_text.parse_description(pre_item_html)

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
        keyword_of_podcasts = func_for_clear_text.parse_keywords(pre_item_html)

    # находим автора, если он есть
    author_of_podcast = str()
    if pre_item_html.find('author>') > -1:
        temp_code = pre_item_html[pre_item_html.find('author>') + 7:]
        author_of_podcast = func_for_clear_text.check_on_shit(temp_code[:temp_code.find('</')])

    # находим категории если они есть
    categorys_of_podcast, subcategorys_of_podcast = func_for_clear_text.parse_category(pre_item_html)

    # print('Название: ' + title_of_podcast + '\n',
    #       'Описание: ' + description_of_podcast + '\n',
    #       'Картинка: ' + image_of_podcasts + '\n',
    #       'Ключевые слова: ' , keyword_of_podcasts , '\n',
    #       'Автор: ' + author_of_podcast + '\n',
    #       'Категории: ' , categorys_of_podcast , '\n',
    #       'Подкатегории: ' , subcategorys_of_podcast , '\n',
    #       )

    util.set_new_podcast(each_podcast, title_of_podcast, description_of_podcast, categorys_of_podcast,
                         image_of_podcasts, author_of_podcast, subcategorys_of_podcast, keyword_of_podcasts)

    """
        Далее идем к выпускам подкаста, именуется этот тег(в плане сам выпуск) в rss как item, 
        и его столько сколько всего выпусков.
        Имеем цикл, который ходит по этим тегам, из каждого тега выкачиваем ввсё что в нём есть.
    """

    html = html[html.find('<item>'):]   # обрезаем весь html до item
    amount_of_item = 0  # кол-во выпусков, качаем не более 50

    while html.find('<item>') > -1 and amount_of_item <= 50:    # до тех пор пока находим новый выпуск
        amount_of_item += 1
        # получаем блок с этим itemом, чтоб работать не по всей странице
        item_code = html[html.find('<item>') + 7: html.find('</item>')]

        # получаем название выпуска
        title_of_item = item_code[item_code.find('<title>') + 7: item_code.find('</title>')]
        title_of_item = func_for_clear_text.check_on_shit(title_of_item)

        # переходим в тег с ссылкой на аудио
        enclosure = item_code[item_code.find('<enclosure'):]
        enclosure = enclosure[enclosure.find('url="') + 5:enclosure.find('/>')]
        mp3 = enclosure[: enclosure.find('"')]  # получаем аудио

        # получаем описание выпуска
        description_of_item = None
        if item_code.find('description') > -1:
            description_of_item = func_for_clear_text.parse_description(item_code)

        # получаем дату публикации выпуска
        pubdata_of_item = func_for_clear_text.clear_pubdata(item_code[item_code.find('<pubDate>') + 14: item_code.find('</pubDate>') - 6])

        # получаем область с длительностью аудио
        duration_of_item = str()
        if item_code.find('duration>') > -1:
            temp_code = item_code[item_code.find('duration>') + 9: item_code.find('duration>') + 20]
            duration_of_item = temp_code[:temp_code.find('</')]    # получаем длительность аудио
            if duration_of_item and duration_of_item.find(':') == -1:     # проверяем разделено ли время : (иначе оно указано в секундах)
                duration_of_item = func_for_clear_text.convert_of_time(int(duration_of_item))

        # получаем картинку выпуска если такова есть
        image_of_item = str()
        if item_code.find('image ') > -1 and item_code.find('"image"') == -1:
            temp_code = item_code[item_code.find('image ') + 6:]
            temp_code = temp_code[temp_code.find('href="') + 6:]
            image_of_item = temp_code[: temp_code.find('"')]

        categorys_of_item, subcategorys_of_item = func_for_clear_text.parse_category(item_code[:item_code.find('</item>')])

        # находим ключевые слова если они есть
        keyword_of_item = str()
        if item_code.find('keywords>') > -1:  # если есть ключевые слова
            keyword_of_item = func_for_clear_text.parse_keywords(item_code[:item_code.find('</item>')])
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
    pre_parse()
