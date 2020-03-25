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
get_podcast_url = lambda status: execute('SELECT * '
                                         'FROM url_podcasts '
                                         'WHERE status_podcast = %(p)s', status)


# существует ли с таким id подкаст
exist_channel = lambda id_channel: execute('SELECT id_podcast '
                                           'FROM podcasts '
                                           'WHERE id_podcast= %(p)s', id_channel)


def set_new_podcast(id_new_podcast, title_podcast, description_podcasts, category_podcast,
                    url_image_podcast, author_podcast, subcat_podcast, keyword_podcast):

    warning = False
    if not title_podcast:
        title_podcast = None
    if not description_podcasts:
        description_podcasts = None
    if not url_image_podcast:
        url_image_podcast = None
        warning = True
    if not author_podcast:
        author_podcast = None

    execute('INSERT INTO podcasts (title_podcast, description_podcast, url_image_podcast, author_podcast, id_podcast, warning) '  # добавляем новый подкаст
            'VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', title_podcast, description_podcasts, url_image_podcast, author_podcast, id_new_podcast, warning,
            commit=True)
    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом

    if len(category_podcast[:-1]) > 0:
        new_categorys = list()
        for category in category_podcast[:-1]:
            if new_categorys.count(category) == 0 and category.startswith('http') is False:
                new_categorys.append(category)

        query_for_get_category = 'SELECT * ' \
                                 'FROM categorys ' \
                                 'WHERE ' + 'title_category IN ("' + '", "'.join(new_categorys) + "\")"

        categorys_already_exist = tuple(execute(query_for_get_category))
        uniq_categorys = tuple(category for category in new_categorys if category not in tuple(row.get('title_category') for row in categorys_already_exist))
        cursor = connect().cursor()
        if uniq_categorys:
            values = tuple((x, x) for x in uniq_categorys).__str__().replace('\'', '\"')[1:-1] if len(uniq_categorys) > 1 else tuple((x, x) for x in uniq_categorys).__str__().replace('\'', '\"')[1:-2]
            cursor.execute('INSERT INTO categorys (title_category, ru_title) VALUES ' + values)
            connect().commit()
            query_for_get_category = 'SELECT * ' \
                                     'FROM categorys ' \
                                     'WHERE ' + 'title_category IN ("' + '", "'.join(uniq_categorys) + "\")"
            categorys_already_exist += tuple(execute(query_for_get_category))

        query_for_connect_all_categorys = 'INSERT INTO podcasts_with_categorys (id_podcast, id_category) VALUES '

        for id_category in tuple(row.get('id_category') for row in categorys_already_exist):
            query_for_connect_all_categorys += '(' + str(id_new_podcast) + ', ' + str(id_category) + '), '

        try:
            cursor.execute(query_for_connect_all_categorys[:-2])
            connect().commit()
        except:
            print('Ошибка связи подкаста с категориями.')
        finally:
            connect().close()

    if len(subcat_podcast[:-1]) > 0:
        new_subcat = list()
        for subcat in subcat_podcast[:-1]:
            if new_subcat.count(subcat) == 0 and subcat.startswith('http') is False and subcat.find('<') == -1:
                new_subcat.append(subcat)

        query_for_get_subcat = 'SELECT * ' \
                               'FROM subcat_podcast ' \
                               'WHERE ' + 'title_subcat IN ("' + '", "'.join(new_subcat) + '")'

        subcat_already_exist = tuple(execute(query_for_get_subcat))     # получаем все подкатегории которые уже есть в бд
        uniq_subcat = tuple(subcat for subcat in new_subcat if subcat not in tuple(row.get('title_subcat') for row in subcat_already_exist))
        # print(new_subcat, uniq_subcat, subcat_already_exist, '=====================================')

        cursor = connect().cursor()
        if uniq_subcat:
            cursor.execute('INSERT INTO subcat_podcast (title_subcat) '
                           'VALUES ("' + '"), ("'.join(uniq_subcat) + '")')
            connect().commit()
            query_for_get_subcat = 'SELECT * ' \
                                   'FROM subcat_podcast ' \
                                   'WHERE ' + 'title_subcat IN ("' + '", "'.join(uniq_subcat) + '")'

            subcat_already_exist += tuple(execute(query_for_get_subcat))

        query_for_connect_all_subcat = 'INSERT INTO podcast_with_subcat (id_podcast, id_subcat) VALUES '
        for id_subcat in tuple(id_subcat for id_subcat in tuple(row.get('id_subcat') for row in subcat_already_exist)):
            query_for_connect_all_subcat += '(' + str(id_new_podcast) + ', ' + str(id_subcat) + '), '

        cursor.execute(query_for_connect_all_subcat[:-2])
        connect().commit()
        connect().close()

    if len(keyword_podcast[:-1]) > 0:
        new_keyword = list()
        if keyword_podcast[-1] == '':
            keyword_podcast = keyword_podcast[:-1]
        for keyword in keyword_podcast:
            if new_keyword.count(keyword) == 0 and keyword.startswith('http') is False:
                new_keyword.append(keyword)

        query_for_get_keyword = 'SELECT * ' \
                                'FROM keywords ' \
                                'WHERE ' + 'title_keyword IN ("' + '", "'.join(new_keyword) + "\")"

        keywords_already_exist = tuple(execute(query_for_get_keyword))
        uniq_keywords = tuple(keyword for keyword in new_keyword if keyword not in tuple(row.get('title_keyword') for row in keywords_already_exist))
        cursor = connect().cursor()

        if uniq_keywords:
            cursor.execute('INSERT INTO keywords (title_keyword) '
                           'VALUES ("' + '"), ("'.join(uniq_keywords) + '")')
            connect().commit()
            query_for_get_keyword = 'SELECT * ' \
                                    'FROM keywords ' \
                                    'WHERE ' + 'title_keyword IN ("' + '", "'.join(uniq_keywords) + '")'

            keywords_already_exist += tuple(execute(query_for_get_keyword))

        query_for_connect_all_keyword = 'INSERT INTO podcasts_with_keywords (id_podcast, id_keyword) VALUES '
        for id_keyword in tuple(id_keyword for id_keyword in tuple(row.get('id_keyword') for row in keywords_already_exist)):
            query_for_connect_all_keyword += '(' + str(id_new_podcast) + ', ' + str(id_keyword) + '), '

        cursor.execute(query_for_connect_all_keyword[:-2])
        connect().commit()
        connect().close()


def check_item(id_podcast, audio):    # проверка на то , есть ли выпуск или нет
    return bool(execute('SELECT title_audio '
                        'FROM items '
                        'WHERE id_podcast = %(p)s '
                        '   AND audio = %(p)s', id_podcast, audio))


def change_url(id_podcast, new_url, status):
    """
        Меняем юрл подкаста, если вдруг он с apple podcast
    """

    if      status > 2 \
            or \
            (len(execute('SELECT * FROM url_podcasts WHERE url_podcast = %(p)s', new_url)) <= 1
             and
            not execute('SELECT * FROM temp_table WHERE new_url = %(p)s', new_url)):
        execute('INSERT INTO temp_table (new_url, status, id) '
                'VALUES (%(p)s, %(p)s, %(p)s)', new_url, status, id_podcast, commit=True)
        return True
    else:
        execute('INSERT INTO temp_table (status, id) '
                'VALUES (%(p)s, %(p)s)', -1, id_podcast,  commit=True)
        return False


def add_url_in_error_links(id_podcast, url, reason):
    """
        Добавляем запись в временную таблицу;
        Добавляем урл в таблицу с ошибками.
    """
    execute('INSERT INTO temp_table (new_url, status, id) '
            'VALUES (%(p)s, %(p)s, %(p)s)', url, -1 , id_podcast, commit=True)
    if not execute('SELECT * '
                   'FROM error_links '
                   'WHERE id = (%(p)s)', id_podcast):
        execute('INSERT INTO error_links (url, id, reason) '
                'VALUES (%(p)s, %(p)s, %(p)s)', url, id_podcast, reason, commit=True)


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

    if query.endswith('VALUE'):   # выпусков НЕТ АЛЛО
        return

    try:
        cursor = connect().cursor()         # открываемванльный коннекшин
        cursor.execute(query)
        connect().commit()
    except Exception as e:
        print('Назакомитились выпуски.')
        connect().close()
        return

    ids = tuple(row.get('id_item') for row in execute('SELECT id_item '
                                                      'FROM items '
                                                      'WHERE id_podcast = %(p)s', id_of_podcast))     # id-шники выпусков

    keywords_used_in_items = tuple()
    for keywords in tuple(item[-1] for item in list_of_items):  # генерируем ключ слова без повторений
        keywords_used_in_items += tuple(set(keyword.replace('"', '""') if keyword.count('"') > 1 else keyword.replace('"', '') for keyword in keywords if keywords_used_in_items.count(keyword) == 0))

    # запрос на получени всех ВОЗМОЖНЫХ слов которые есть в выпуске и есть в бд, по ним же потом и будем отсекать лишнее
    query_for_get = 'SELECT * ' \
                    'FROM keywords_items ' \
                    'WHERE ' + 'title_keyword IN ("' + '", "'.join(keywords_used_in_items) + '")'

    try:
        keywords_already_in_db = tuple(execute(query_for_get))
    except Exception as e:
        connect().close()
    else:
        uniq_words = tuple(keyword for keyword in keywords_used_in_items if keyword not in tuple(row.get('title_keyword') for row in keywords_already_in_db))      # получаем слова которых НЕТ в бд то есть новые

        if uniq_words:  # если уникальные слова всё-таки есть
            try:
                cursor.execute(str('INSERT INTO keywords_items (title_keyword) '
                                   'VALUES ("' + '"), ("'.join(uniq_words) + '"), ("')[:-4])
                connect().commit()
            except Exception as e:
                print('Ошибка в инсерте ключевых слов.')
                connect().close()   # если вдруг что-то пошло не так, ОБЯЗАТЕЛЬНО ЗАКРЫВАЕМ конекшин
                return
            # запрос на получение айди только НОВЫХ ключ. слов, то есть тех которые были добавленны благодаря новым выпускам
            query_for_get = 'SELECT * ' \
                            'FROM keywords_items ' \
                            'WHERE ' + 'title_keyword IN ("' + '", "'.join(uniq_words) + '")'
            keywords_already_in_db += tuple(execute(query_for_get))

        ids_of_new_words = {row.get('title_keyword'): row.get('id_keyword_item') for row in keywords_already_in_db}  # айди всех новых слов
        query_for_connect_all = 'INSERT INTO items_with_keywords (id_item, id_keyword ) VALUES '
        for item in enumerate(list_of_items):   #
            if item[1][-1]:
                tuple_with_id_keywords = tuple(str(ids_of_new_words.get(keyword)) for keyword in item[1][-1])    # генерируем по словам айдишники
                query_for_connect_all += '(' + str(ids[item[0]]) + ', ' + '), ({}, '.format(str(ids[item[0]])).join(tuple_with_id_keywords) + '), '

        if len(query_for_connect_all[:-2]) != 60:   # если вдруг будет вылетать ошибка
            try:
                cursor.execute(query_for_connect_all[:-2])
            except Exception as e:
                print('Проблема в коннекте ключ. слов и выпуска.')
                connect().close()
            else:
                connect().commit()

        connect().close()


change_status = lambda url, status, id_podcast:execute('INSERT INTO temp_table(new_url, status, id) '
                                                       'VALUES(%(p)s, %(p)s, %(p)s)', url, status, id_podcast, commit=True)
