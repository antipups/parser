import re


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
    # print('====================================\n')
    # print(string)
    if string.find('<p') > -1:
        temp_str = string[string.find('<p'):]
        string = string.replace(temp_str[:temp_str.find('>') + 1], '')
    if string.find('<br />') > -1:
        string = string.replace('<br />', '')
    if string.find('<a href="') > -1:
        if string.find('<a href="') == 0:
            string = string[string.find('">') + 2:] + ' '
        else:
            string = string[:string.find('<a href')] + string[string.find('">') + 2:] + ' '
    if string.find('<strong>') > -1:
        string = string.replace('<strong>', '')
    if string.find('<span') > -1:
        temp_str = string[string.find('<span'):]
        string = string.replace(temp_str[:temp_str.find('>') + 1], '')
    if string.find('<ul>') > -1:
        string = string.replace('<ul>', '\n')
        string = string.replace('<li>', '\n')
    if string.find('<ol>') > -1:
        string = string.replace('<ol>', '\n')
        string = string.replace('<li>', '\n')
    if string.find('<u>') > -1:
        string = string.replace('<u>', '')
    if string.find('<div') > -1:
        temp_str = string[string.find('<div'):]
        string = string.replace(temp_str[:temp_str.find('>') + 1], '')
    # print(string)
    # print('\n====================================')
    return string


def convert_time(time):      # конвертация времени из секунд в часы
    return ('0' * (2 - len(str(time // 3600))) + str(time // 3600)) + ':' + ('0' * (2 - len(str(time // 60 % 60))) + str(time // 60 % 60)) + ':' + ('0' * (2 - len(str(time % 60))) + str(time % 60))


def parse_category(html):   # парсим категории
    categorys, subcategorys = str(), str()
    while html.find('category ') > -1:  # считываем все категории
        html = html[html.find('category text="') + 15:]
        if html.find('>') < html.find('/>'):  # если у категории есть подкатегории
            categorys += html[: html.find('"')] + ', '
            subcategorys_field = html[html.find('>') + 1: html.find('</itunes:category>')]
            while subcategorys_field.find('category text="') > -1:
                subcategorys += subcategorys_field[subcategorys_field.find('category text="') + 15: subcategorys_field.rfind('"')]  + ', '
                subcategorys_field = subcategorys_field[subcategorys_field.find('/>') + 2:]
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
    # print(temp_code[: temp_code.find('</')])
    return check_on_shit(temp_code[: temp_code.find('</')])


def clear_pubdata(string):
    dict_day = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                   'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    if string[1] == ' ':    # для нормального времени (2 -> 02)
        string = '0' + string[0] + ' ' + string[2:]
    month = re.search(r'\w\w\w', string)[0]
    string = re.sub(month, dict_day.get(month), string)  # запуливаем вместо названия месяца номер месяца
    string = re.sub(r'[ :]', '', string)    # вместо пробела и двоиточия ничего, в инт бахаем
    return string[4:8] + string[2:4] + string[:2] + string[-6:]   # подводим под шаблон бд