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

    change_of_status(url_of_podcast, 2)     # меняем статус на статус полной докачки

    # print(title_of_podcast, description_of_podcasts, url_of_image_of_podcast, author_of_podcast, 1,)
    execute('INSERT INTO podcasts (title_of_podcast, description_of_podcast, url_of_image_of_podcast, author_of_podcast) '  # добавляем новый подкаст
            'VALUES (%(p)s, %(p)s, %(p)s, %(p)s)', title_of_podcast, description_of_podcasts, url_of_image_of_podcast, author_of_podcast,
            commit=True)

    # получаем id нового подкаста для скачки тегов и категорий
    id_of_new_podcast = execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s',
                                title_of_podcast)[0].get('id_of_podcast')

    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом
    for each_category in category_of_podcast:
        if not each_category:    # после обрезки, последний элемент - всегда пуст
            break
        if not execute('SELECT id_of_category FROM categorys WHERE title_of_category = %(p)s', each_category):
            execute('INSERT INTO categorys(title_of_category) VALUES (%(p)s)', each_category, commit=True)   # если нет такой категории, создаем
            id_of_new_category = execute('SELECT id_of_category FROM categorys '
                                         'WHERE title_of_category = %(p)s',
                                         each_category)[0].get('id_of_category')  # находим новую категорию и записываем её
            execute('INSERT INTO podcasts_with_categorys(id_of_podcast, id_of_category) '
                    'VALUES (%(p)s, %(p)s)', id_of_new_podcast, id_of_new_category, commit=True)    # привязываем подкаст к этой категории
        else:
            id_of_category = execute('SELECT id_of_category FROM categorys WHERE title_of_category = %(p)s',
                                     each_category)[0].get('id_of_category')
            execute('INSERT INTO podcasts_with_categorys(id_of_category, id_of_podcast) VALUES (%(p)s, %(p)s)',
                    id_of_category, id_of_new_podcast, commit=True)

    for each_subcategory in subcat_of_podcast:   # добавляем подкатегории к подкасту
        if each_subcategory:   # во время срезки выходит пустая строка, доп проверка на неё
            execute('INSERT INTO subcat_of_podcast(id_of_podcast, title_of_subcat) VALUES (%(p)s, %(p)s)',
                    id_of_new_podcast, each_subcategory, commit=True)

    for each_keyword in keyword_of_podcast:  # тот же алгоритм что и с категориями
        if not each_keyword:
            break
        if not execute('SELECT id_of_keyword FROM keywords WHERE title_of_keyword = %(p)s', each_keyword):
            execute('INSERT INTO keywords (title_of_keyword) VALUES (%(p)s)', each_keyword, commit=True)
            id_of_new_keyword = execute('SELECT id_of_keyword FROM keywords WHERE title_of_keyword = %(p)s',
                                        each_keyword)[0].get('id_of_keyword')
            execute('INSERT INTO podcasts_with_keywords (id_of_podcast, id_of_keyword) VALUES (%(p)s, %(p)s)',
                    id_of_new_podcast, id_of_new_keyword, commit=True)
        else:
            id_of_keyword = execute('SELECT id_of_keyword FROM keywords WHERE title_of_keyword = %(p)s',
                                    each_keyword)[0].get('id_of_keyword')
            execute('INSERT INTO podcasts_with_keywords (id_of_podcast, id_of_keyword) VALUES (%(p)s, %(p)s)',
                    id_of_new_podcast, id_of_keyword, commit=True)


def check_item(title_of_item, title_of_podcast, audio):    # проверка на то , есть ли выпуск или нет
    if not execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s', title_of_podcast):
        return False
    id_of_podcast = execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s', title_of_podcast)[0].get('id_of_podcast')
    return execute('SELECT title_of_audio FROM items WHERE id_of_podcast = %(p)s AND '
                   'title_of_audio = %(p)s AND audio = %(p)s', id_of_podcast, title_of_item, audio)


def set_new_item(title_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio, pubdata_of_audio,
                 duration_of_audio, category_of_item, subcategory_of_item, keyword_of_item):

    id_of_podcast = execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s', title_of_podcast)[0].get('id_of_podcast')
    if not duration_of_audio:
        duration_of_audio = None
    if not image_of_audio:
        image_of_audio = None
    if not pubdata_of_audio:
        pubdata_of_audio = None
    try:
        execute('INSERT INTO items (id_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio, pubdata_of_audio, duration_of_audio)'
                ' VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', id_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio,
                pubdata_of_audio, duration_of_audio, commit=True)
    except IndexError:
        print('Ошибка, не коммитит')
        return
    try:
        id_of_item = execute('SELECT id_of_item FROM items WHERE title_of_audio = %(p)s '
                             'AND id_of_podcast = %(p)s', title_of_audio, id_of_podcast)[0].get('id_of_item')
    except IndexError:
        print('Незакомитило')
        return

    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом
    for each_category in category_of_item:
        if not each_category:    # после обрезки, последний элемент - всегда пуст
            break
        else:
            execute('INSERT INTO cat_of_item(id_of_item, category) '
                    'VALUES (%(p)s, %(p)s)', id_of_item, each_category,
                    commit=True)  # привязываем подкаст к этой категории

    for each_subcategory in subcategory_of_item:
        if not each_subcategory:    # после обрезки, последний элемент - всегда пуст
            break
        else:
            execute('INSERT INTO subcat_of_item(id_of_item, title_of_subcategory) '
                    'VALUES (%(p)s, %(p)s)', id_of_item, each_subcategory,
                    commit=True)  # привязываем подкаст к этой категории

    for each_keyword in keyword_of_item:
        if not each_keyword:
            break
        if not execute('SELECT id_of_keyword_of_item FROM keywords_of_items WHERE title_of_keyword = %(p)s', each_keyword):
            execute('INSERT INTO keywords_of_items (title_of_keyword) VALUES (%(p)s)', each_keyword, commit=True)
            id_of_new_keyword = execute('SELECT id_of_keyword_of_item FROM keywords_of_items WHERE title_of_keyword = %(p)s',
                                        each_keyword)[0].get('id_of_keyword_of_item')
            execute('INSERT INTO items_with_keywords (id_of_item , id_of_keyword) VALUES (%(p)s, %(p)s)',
                    id_of_item, id_of_new_keyword, commit=True)
        else:
            id_of_keyword = execute('SELECT id_of_keyword_of_item FROM keywords_of_items WHERE title_of_keyword = %(p)s',
                                        each_keyword)[0].get('id_of_keyword_of_item')
            execute('INSERT INTO podcasts_with_keywords (id_of_podcast, id_of_keyword) VALUES (%(p)s, %(p)s)',
                    id_of_podcast, id_of_keyword, commit=True)


def change_of_status(url_of_podcast, status):   # смена статуса
    execute('UPDATE url_of_podcasts SET status_of_podcast = %(p)s WHERE url_of_podcast = %(p)s',
            status,  url_of_podcast, commit=True)

