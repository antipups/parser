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


def check_new_podcast():
    return execute('SELECT * FROM url_of_podcasts')


def set_new_podcast(url_of_podcast, title_of_podcast, description_of_podcasts, category_of_podcast,
                    url_of_image_of_podcast, author_of_podcast, subcat_of_podcast, keyword_of_podcast):
    if execute('SELECT title_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s', title_of_podcast):   # проверяем есть ли подкаст уже в бд
        return
    execute('UPDATE url_of_podcasts SET download = 0 WHERE url_of_podcast = %(p)s', url_of_podcast, commit=True)    # ставим подкасту 0, что мы его уже скачали

    execute('INSERT INTO podcasts (title_of_podcast, description_of_podcast, url_of_image_of_podcast, author_of_podcast) '  # добавляем новый подкаст
            'VALUES (%(p)s, %(p)s, %(p)s, %(p)s)', title_of_podcast, description_of_podcasts, url_of_image_of_podcast, author_of_podcast,
            commit=True)

    # получаем id нового подкаста для скачки тегов и категорий
    id_of_new_podcast = execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s',
                                title_of_podcast)[0].get('id_of_podcast')

    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом
    for eachcategory in category_of_podcast:
        if not eachcategory:    # после обрезки, последний элемент - всегда пуст
            break
        if not execute('SELECT id_of_category FROM categorys WHERE title_of_category = %(p)s', eachcategory):
            execute('INSERT INTO categorys(title_of_category) VALUES (%(p)s)', eachcategory, commit=True)   # если нет такой категории, создаем
            id_of_new_category = execute('SELECT id_of_category FROM categorys '
                                         'WHERE title_of_category = %(p)s',
                                         eachcategory)[0].get('id_of_category')  # находим новую категорию и записываем её
            execute('INSERT INTO podcasts_with_categorys(id_of_podcast, id_of_category) '
                    'VALUES (%(p)s, %(p)s)', id_of_new_podcast, id_of_new_category, commit=True)    # привязываем подкаст к этой категории
        else:
            id_of_category = execute('SELECT id_of_category FROM categorys WHERE title_of_category = %(p)s',
                                     eachcategory)[0].get('id_of_category')
            execute('INSERT INTO podcasts_with_categorys(id_of_category, id_of_podcast) VALUES (%(p)s, %(p)s)',
                    id_of_category, id_of_new_podcast, commit=True)

    for eachsubcategory in subcat_of_podcast:   # добавляем подкатегории к подкасту
        if eachsubcategory:   # во время срезки выходит пустая строка, доп проверка на неё
            execute('INSERT INTO subcat_of_podcast(id_of_podcast, title_of_subcat) VALUES (%(p)s, %(p)s)',
                    id_of_new_podcast, eachsubcategory, commit=True)

    for eachkeyword in keyword_of_podcast:  # тот же алгоритм что и с категориями
        if not eachkeyword:
            break
        if not execute('SELECT id_of_keyword FROM keywords WHERE title_of_keyword = %(p)s', eachkeyword):
            execute('INSERT INTO keywords (title_of_keyword) VALUES (%(p)s)', eachkeyword, commit=True)
            id_of_new_keyword = execute('SELECT id_of_keyword FROM keywords WHERE title_of_keyword = %(p)s',
                                        eachkeyword)[0].get('id_of_keyword')
            execute('INSERT INTO podcasts_with_keywords (id_of_podcast, id_of_keyword) VALUES (%(p)s, %(p)s)',
                    id_of_new_podcast, id_of_new_keyword, commit=True)
        else:
            id_of_keyword = execute('SELECT id_of_keyword FROM keywords WHERE title_of_keyword = %(p)s',
                                    eachkeyword)[0].get('id_of_keyword')
            execute('INSERT INTO podcasts_with_keywords (id_of_podcast, id_of_keyword) VALUES (%(p)s, %(p)s)',
                    id_of_new_podcast, id_of_keyword, commit=True)


def set_new_item(title_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio, pubdata_of_audio, duration_of_audio):
    id_of_podcast = execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s', title_of_podcast)[0].get('id_of_podcast')
    execute('INSERT INTO items (id_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio, pubdata_of_audio, duration_of_audio)'
            ' VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', id_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio,
            pubdata_of_audio, duration_of_audio, commit=True)

