import pymysql.cursors
import config

paramstyle = "%s"


def deploy_database():
    """
     Создать нужные таблицы в базе данных
    """
    pass


def connect():
    """
     Подключение к базе данных
    """
    return pymysql.connect(
        config.db_host,
        config.db_user,
        config.db_password,
        config.db_database,
        use_unicode=True,
        charset=config.db_charset,
        cursorclass=pymysql.cursors.DictCursor)


def execute(sql, *args, commit=False):
    """
     Формат запроса:
     execute('<Запрос>', <передаваемые параметры>, <commit=True>)
    """
    db = connect()
    cur = db.cursor()
    try:
        cur.execute(sql % {"p": paramstyle}, args)
    except pymysql.err.InternalError as e:
        if sql.find('texts') == -1:
            print('Cannot execute mysql request: ' + str(e))
        return
    if commit:
        db.commit()
        db.close()
    else:
        ans = cur.fetchall()
        db.close()
        return ans


#   получаем все подкасты одного статуса
get_podcast_url = lambda status: execute('SELECT * FROM url_podcasts WHERE status_podcast = %(p)s', status)


# существует ли с таким id подкаст
exist_channel = lambda id_channel: execute('SELECT id_podcast FROM podcasts WHERE id_podcast= %(p)s', id_channel)


def set_new_podcast(id_new_podcast, url_podcast, title_podcast, description_podcasts, category_podcast,
                    url_image_podcast, author_podcast, subcat_podcast, keyword_podcast):

    change_status(url_podcast, 2)     # меняем статус на статус полной докачки

    warning = False
    if not description_podcasts:
        description_podcasts = 'NULL'
    if not url_image_podcast:
        url_image_podcast = 'NULL'
        warning = True
    if not author_podcast:
        author_podcast = 'NULL'

    execute('INSERT INTO podcasts (title_podcast, description_podcast, url_image_podcast, author_podcast, id_podcast, warning) '  # добавляем новый подкаст
            'VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', title_podcast, description_podcasts, url_image_podcast, author_podcast, id_new_podcast, warning,
            commit=True)
    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом

    #sql =  SELECT * FROM ... WHERE title_category IN (СЮДА СПИСОК ВСЕХ КАТЕГОРИЙ ЧЕРЕЗ ЗАПЯТУЮ)
    # for data in sql удаляем категории из списка и потом их инзертим списком
    for each_category in category_podcast[:-1]:
        if each_category:
            if each_category.startswith('http'):
                continue

            category = execute('SELECT id_category FROM categorys WHERE title_category = %(p)s', each_category)
            if not category:
                execute('INSERT INTO categorys(title_category, ru_title) VALUES (%(p)s, %(p)s)', each_category, each_category, commit=True)   # если нет такой категории, создаем
                id_category = execute('SELECT id_category FROM categorys '
                                      'WHERE title_category = %(p)s',
                                       each_category)[0].get('id_category')  # находим новую категорию и записываем её
            else:
                id_category = category[0].get('id_category')

            if not execute('SELECT * FROM podcasts_with_categorys WHERE id_podcast = %(p)s AND id_category = %(p)s',    # если данной связки ещё нет
                           id_new_podcast, id_category):

                execute('INSERT INTO podcasts_with_categorys(id_category, id_podcast) VALUES (%(p)s, %(p)s)',
                        id_category, id_new_podcast, commit=True)

    for each_subcategory in subcat_podcast:   # добавляем подкатегории к подкасту
        if each_subcategory:   # во время срезки выходит пустая строка, доп проверка на неё
            subcat = execute('SELECT * FROM subcat_podcast WHERE title_subcat = (%(p)s)', each_subcategory)
            if not subcat:
                execute('INSERT INTO subcat_podcast (title_subcat) VALUES (%(p)s)', each_subcategory, commit=True)
                id_subcat = execute('SELECT * FROM subcat_podcast WHERE title_subcat = (%(p)s)', each_subcategory)[0].get('id_subcat')
            else:
                id_subcat = subcat[0].get('id_subcat')

            execute('INSERT INTO podcast_with_subcat(id_podcast, id_subcat) VALUES (%(p)s, %(p)s)',
                    id_new_podcast, id_subcat, commit=True)

    for each_keyword in keyword_podcast[:-1]:  # тот же алгоритм что и с категориями
        if each_keyword:
            each_keyword = each_keyword.lower()
            keyword = execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s', each_keyword)

            if not keyword:

                execute('INSERT INTO keywords (title_keyword) VALUES (%(p)s)', each_keyword, commit=True)
                id_keyword = execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s',
                                            each_keyword)[0].get('id_keyword')
            else:
                id_keyword = keyword[0].get('id_keyword')

            if not execute('SELECT * FROM podcasts_with_keywords WHERE id_podcast = %(p)s AND id_keyword = %(p)s',
                           id_new_podcast, id_keyword):
                execute('INSERT INTO podcasts_with_keywords (id_podcast, id_keyword) VALUES (%(p)s, %(p)s)',
                        id_new_podcast, id_keyword, commit=True)

    return id_new_podcast


def check_item(title_item, title_podcast, audio):    # проверка на то , есть ли выпуск или нет
    podcast = execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast)
    if not podcast:
        return False
    id_podcast = podcast[0].get('id_podcast')
    return bool(execute('SELECT title_audio FROM items WHERE id_podcast = %(p)s AND '
                        'title_audio = %(p)s AND audio = %(p)s', id_podcast, title_item, audio))


def change_status(url_podcast, status):
    """
        Меняем статус подкаста, передаем:
            1 - если нужна начальная инфа;
            2 - если нужна полная докачка;
            3 - если нужна докачкка последних выпусков
    """
    execute('UPDATE url_podcasts SET status_podcast = %(p)s WHERE url_podcast = %(p)s',
            status,  url_podcast, commit=True)


def change_url(new_url, old_url):
    """
        Меняем юрл подкаста, если вдруг он с apple podcast
    """
    if not execute('SELECT * FROM url_podcasts WHERE url_podcast = %(p)s', new_url):
        execute('UPDATE url_podcasts SET url_podcast = %(p)s WHERE url_podcast = %(p)s',
                new_url, old_url, commit=True)
    else:
        execute('DELETE FROM url_podcasts WHERE url_podcast = %(p)s', old_url, commit=True)


def add_url_in_error_links(url, reason=None):
    """
        Добавляем url в таблицу error link, и удаляем её из основной
    """
    execute('DELETE FROM url_podcasts WHERE url_podcast = %(p)s', url, commit=True)
    if not execute('SELECT * FROM error_links WHERE (%(p)s)', url):
        execute('INSERT INTO error_links (url, reason) VALUES (%(p)s, %(p)s)', url, reason, commit=True)


def set_new_item(id_of_podcast, list_of_items):
    """
        Функция которая добавляет в БД сразу несколько выпусков.
    :param id_of_podcast:       айди подкаста, полученный раннее, к нему и будет привязаны выпуски
    :param list_of_items:       список выпусков которые будут добавленны в бд
    :return:                    возвращаем все айди добавленных выпусков
    """

    query = 'INSERT INTO items (id_podcast, title_audio, description_audio, audio, image_audio, pubdata_audio, duration_audio) ' \
            'VALUES '       # строка на дополнение к запросу

    for item in list_of_items:
        title, description, audio, image, pubdata, duration = item[:-1]     # именуем все полученные элементы (чтоб с ними было удобней работать)

        # если ничего нет - зануляем
        description = 'NULL' if not description else '"' + description + '"'
        image = 'NULL' if not image else '"' + image + '"'
        duration = 'NULL' if not duration else '"' + duration + '"'
        pubdata = 'NULL' if not pubdata else '"' + pubdata + '"'
        audio = 'NULL' if not audio else '"' + audio + '"'

        if title.find('"') > -1:
            title = title.replace('"', '""')
        if description and description.find('"') > -1:
            description = description.replace('"', '""')[1:-1]
        query += '({}, "{}", {}, {}, {}, {}, {}), '.format(id_of_podcast, title, description, audio, image, pubdata, duration)
    else:
        query = query[:-2]

    try:
        cursor = connect().cursor()         # открываемванльный коннекшин
        cursor.execute(query)
        connect().commit()

    except Exception as e:
        print('Error in sql syntax', e)

    ids = tuple(row.get('id_item') for row in execute('SELECT id_item FROM items WHERE id_podcast = %(p)s', id_of_podcast))     # id-шники выпусков

    query_for_insert_keywords = 'INSERT INTO keywords_items (title_keyword) VALUES ("'
    new_words = set()
    for keywords in tuple(item[-1] for item in list_of_items):  # генерируем ключ слова без повторений
        new_words = new_words.union(set(keywords))

    query_for_get = 'SELECT * ' \
                    'FROM ' \
                    'keywords_items WHERE ' + 'title_keyword = "' + '" OR title_keyword = "'.join(new_words) + '"'

    uniq_words = new_words.difference(set(row.get('title_keyword') for row in execute(query_for_get)))      # получаем слова которых НЕТ в бд то есть новые
    query_for_insert_keywords += '"), ("'.join(uniq_words) + '"), ("'   # создаем запрос только с НОВЫМИ словами

    if len(query_for_insert_keywords) > 52:     # если ключевые слова есть
        try:
            cursor.execute(query_for_insert_keywords[:-4])
            connect().commit()
        except Exception as e:
            print('Error')
            return

    ids_of_new_words = {row.get('title_keyword'): row.get('id_keyword_item') for row in execute(query_for_get)}  # айди всех новых слов
    query_for_connect_all = 'INSERT INTO items_with_keywords (id_item, id_keyword ) VALUES '
    for item in enumerate(list_of_items):   #
        if item[1][-1]:
            tuple_with_id_keywords = tuple(str(ids_of_new_words.get(keyword)) for keyword in item[1][-1])    # генерируем по словам айдишники
            query_for_connect_all += '(' + str(ids[item[0]]) + ', ' + '), ({}, '.format(str(ids[item[0]])).join(tuple_with_id_keywords) + '), '

    if len(query_for_connect_all) > 62:
        cursor.execute(query_for_connect_all[:-2])
        connect().commit()

    connect().close()
