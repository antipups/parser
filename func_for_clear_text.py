import re


def check_on_shit(string):      # чистим полученные строки от говна, типа сидата или спецсимволы хтмл
    if string.find('&#') > -1:
        string = encode_from_html(string)
    if string.find('<![CDATA[') > -1:   # чистим строку от cdata
        string = string[string.find('<![CDATA[') + 9: string.find(']]>')]
    string = clear_from_tags(string)
    return string


def encode_from_html(string):   # перекодировка из html символов в обычные
    while re.search(r'&#\d{1,4};', string) is not None:     # чистим от цифр, заменяя буквами если вохможно (&#1044;)
        swap_word = re.search(r'&#\d{1,4};', string).group()    # копируем изменяемое слово
        if len(swap_word) != 7 or not 1040 <= int(swap_word[-5:-1]) <= 1103:  # все слова которые не буквы, меняем на пробел
            new_word = ' '
        else:
            new_word = chr(int(re.search(swap_word, string).group()[-5:-1]))
        string = re.sub(swap_word, new_word, string)

    while re.search(r'&\w{1,8};', string) is not None:  # чистим от кода на буквах (&amp;)
        string = re.sub(re.search(r'&\w{1,8};', string).group(), '', string)
    return string


def clear_from_tags(string):
    if re.search(r'&lt;|&gt;|quot;', string):
        string = string.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    if re.search(r"</?p[^</]*>", string) is not None:
        string = re.sub(r"</?p[^</]*>", '\n', string)
    if re.search(r"<['/', ' ']{0,2}br['/', ' ']{0,2}>", string) is not None:
        string = re.sub(r"<['/', ' ']{0,2}br['/', ' ']{0,2}>", '\n', string)
    if string.find('<strong>') > -1:
        string = string.replace('<strong>', '').replace('</strong>', '')
    while string.find('<a') > -1:
        temp_str = string[string.find('<a'):string.find('</a>') + 4]
        if len(temp_str) < 2:   # кастыль, ну а что сделаешь
            break
        url = None
        if temp_str.find('href') > -1 or temp_str.find('HREF') > -1:
            url = temp_str[temp_str.find(re.search(r'href\s?=\s?"', string, flags=re.IGNORECASE).group()) + len(re.search(r'href\s?=\s?"', string, flags=re.IGNORECASE).group()):]
            url = url[:url.find('"')]   # тупо ссылка которая в href
        content = temp_str[temp_str.find('>') + 1:temp_str.find('</a>')]    # контент котоорый в теле тега <a>
        if content == url:
            string = string.replace(temp_str, ' ' + url)
        else:
            if url is not None:
                string = string.replace(temp_str, ' ' + url + ' - ' + content)
            else:
                string = string.replace(temp_str, content)
    if re.search(r"<span[^</]*>", string) is not None:
        for i in re.findall(r"</?span[^</]*>", string):
            string = string.replace(i, ' ')
    if string.find('<ul>') > -1:
        string = re.sub(r"<(/?ul)>", '', string)
    if string.find('<ol>') > -1:
        string = re.sub(r"<(/?ol)>", '', string)
    if re.search(r"</?li[^>]*>", string) is not None:
        string = re.sub(r"</?li[^>]*>", '\n', string)
    if string.find('<u>') > -1:
        string = re.sub(r"</?u>", '', string)
    if re.search(r"<['/', ' ']{0,2}hr['/', ' ']{0,2}>", string) is not None:
        string = re.sub(r"<['/', ' ']{0,2}hr['/', ' ']{0,2}>", '\n', string)
    if string.find('<div') > -1:
        string = re.sub(r"<div[^>]*</div>", '', string)
    if re.search(r"<img[^>]*/>", string) is not None:
        string = re.sub(r"<img[^>]*/>", '', string)
    if re.search(r"<h[^>]>", string) is not None:
        string = re.sub(r"</?h[^>]>", '', string)
    if re.search(r"</?b>", string) is not None:
        string = re.sub(r"</?b>", '', string)
    if re.search(r"<(/?tr|/?td)>", string) is not None:
        string = re.sub(r"<(/?tr|/?td)>", '', string)
    if re.search(r"</?table[^>]*>", string) is not None:
        string = re.sub(r"</?table[^>]*>", '', string)
    if re.search(r"&(nbsp|amp);", string) is not None:
        string = re.sub(r"&(nbsp|amp);", '', string)
    if string.find('<em') > -1:
        string = re.sub(r"</?em>", '', string, flags=re.IGNORECASE)
    if string.find('<code') > -1:
        string = re.sub(r"</?code>", '', string)
    return string


def convert_time(time):      # конвертация времени из секунд в часы
    return ('0' * (2 - len(str(time // 3600))) + str(time // 3600)) + ':' + ('0' * (2 - len(str(time // 60 % 60))) + str(time // 60 % 60)) + ':' + ('0' * (2 - len(str(time % 60))) + str(time % 60))


def parse_category(html):   # парсим категории
    categorys, subcategorys = str(), str()
    while html.find('category ') > -1:  # считываем все категории
        if html.find('category text="') == -1:
            break
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
    if html.find('description>') == -1:
        return None
    temp_code = html[html.find('description>') + 12:]
    return check_on_shit(temp_code[:temp_code.find(re.search(r"</(desc|itun)", temp_code).group())])


def clear_pubdata(string):
    dict_day = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                   'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    if string[1] == ' ':    # для нормального времени (2 -> 02)
        string = '0' + string[0] + ' ' + string[2:]
    month = re.search(r'\w\w\w', string).group()
    if dict_day.get(month) is None:
        return None
    string = re.sub(month, dict_day.get(month), string)  # запуливаем вместо названия месяца номер месяца
    string = re.sub(r'[ :]', '', string)    # вместо пробела и двоиточия ничего, в инт бахаем
    return string[4:8] + string[2:4] + string[:2] + string[-6:]   # подводим под шаблон бд