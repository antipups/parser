import threading
import requests
import util
import func_for_clear_text


def pre_parse():
    """
        Фукнкция которая парсит все url'ы с бд, и под каждый url выделяет поток, после чего парсит
        с url'a инфу.
    """
    for each_podcast in util.check_new_podcast():  # проходимся по ВСЕМ подкастам
        # threading.Thread(target=parse, args=(each_podcast.get('url_podcast'), )).start()
        parse(each_podcast.get('url_podcast'))


def parse(each_podcast):
    """
            Берем с бд все ссылки на подкасты, проходимся по ним, если у подкаста метка 3, то не качаем его инфу,
        а сразу переходим к выпускам, качаем до тех пор, пока не найдем скаченный выпуск.
    """

    html = requests.get(each_podcast).content.decode('utf-8')     # получаем саму ленту
    pre_item_html = html[:html.find('<item>')]      # записываем в ленте часть перед выпусками (для быстрдействия?)

    # находим название подкаста
    title_podcast = pre_item_html[pre_item_html.find('<title>') + 7: pre_item_html.find('</title>')]
    title_podcast = func_for_clear_text.check_on_shit(title_podcast)  # название пригодится при парсинге выпуском

    html = html[html.find('<item>'):]   # обрезаем весь html до item

    while html.find('<item>') > -1:    # до тех пор пока находим новый выпуск
        # получаем блок с этим itemом, чтоб работать не по всей странице
        item_code = html[html.find('<item>') + 7: html.find('</item>')]

        # получаем название выпуска
        title_item = item_code[item_code.find('<title>') + 7: item_code.find('</title>')]
        title_item = func_for_clear_text.check_on_shit(title_item)

        # переходим в тег с ссылкой на аудио
        enclosure = item_code[item_code.find('<enclosure'):]
        enclosure = enclosure[enclosure.find('url="') + 5:enclosure.find('/>')]
        mp3 = enclosure[: enclosure.find('"')]  # получаем аудио

        if util.check_item(title_item, title_podcast, mp3):    # если такой выпуск уже есть, выходим
            return

        # получаем описание выпуска
        description_item = None
        if item_code.find('description') > -1:
            description_item = func_for_clear_text.parse_description(item_code)

        # получаем дату публикации выпуска
        pubdata_item = func_for_clear_text.clear_pubdata(item_code[item_code.find('<pubDate>') + 14: item_code.find('</pubDate>') - 6])

        # получаем область с длительностью аудио
        duration_item = str()
        if item_code.find('duration>') > -1:
            temp_code = item_code[item_code.find('duration>') + 9: item_code.find('duration>') + 20]
            duration_item = temp_code[:temp_code.find('</')]    # получаем длительность аудио
            if duration_item and duration_item.find(':') == -1:     # проверяем разделено ли время : (иначе оно указано в секундах)
                duration_item = func_for_clear_text.convert_time(int(duration_item))

        # получаем картинку выпуска если такова есть
        image_item = str()
        if item_code.find('image ') > -1 and item_code.find('"image"') == -1:
            temp_code = item_code[item_code.find('image ') + 6:]
            temp_code = temp_code[temp_code.find('href="') + 6:]
            image_item = temp_code[: temp_code.find('"')]

        categorys_item, subcategorys_item = func_for_clear_text.parse_category(item_code[:item_code.find('</item>')])

        # находим ключевые слова если они есть
        keyword_item = str()
        if item_code.find('keywords>') > -1:  # если есть ключевые слова
            keyword_item = func_for_clear_text.parse_keywords(item_code[:item_code.find('</item>')])
        util.set_new_item(title_podcast, title_item, description_item, mp3, image_item,
                          pubdata_item, duration_item, categorys_item, subcategorys_item, keyword_item)
        html = html[html.find('</item>') + 7:]   # режем ту строку с которой отработали, и идем далее
        # print('Название выпуска: ' + title_item + '\n',
        #       'Описание выпуска: ' + description_item + '\n',
        #       'Музыка: ' + mp3 + '\n',
        #       'Дата публикации выпуска: ' + pubdata_item + '\n',
        #       'Длительность выпуска: ' + duration_item + '\n',
        #       'Картинка выпуска: ' + image_item + '\n',
        #       'Категории выпуска: ', categorys_item , '\n',
        #       'Подкатегории выпуска: ', subcategorys_item , '\n',
        #       'Ключевые слова выпуска: ', keyword_item , '\n',
        #       )


if __name__ == '__main__':
    pre_parse()
