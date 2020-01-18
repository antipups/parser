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
    return execute('SELECT * FROM url_podcasts')


def set_new_podcast(url_podcast, title_podcast, description_podcasts, category_podcast,
                    url_image_podcast, author_podcast, subcat_podcast, keyword_podcast):

    change_status(url_podcast, 2)     # меняем статус на статус полной докачки

    # print(title_of_podcast, description_of_podcasts, url_of_image_of_podcast, author_of_podcast, 1,)
    execute('INSERT INTO podcasts (title_podcast, description_podcast, url_image_podcast, author_podcast) '  # добавляем новый подкаст
            'VALUES (%(p)s, %(p)s, %(p)s, %(p)s)', title_podcast, description_podcasts, url_image_podcast, author_podcast,
            commit=True)

    # получаем id нового подкаста для скачки тегов и категорий
    id_new_podcast = execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s',
                                title_podcast)[0].get('id_podcast')

    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом
    for each_category in category_podcast:
        if not each_category:    # после обрезки, последний элемент - всегда пуст
            break
        if not execute('SELECT id_category FROM categorys WHERE title_category = %(p)s', each_category):
            execute('INSERT INTO categorys(title_category) VALUES (%(p)s)', each_category, commit=True)   # если нет такой категории, создаем
            id_new_category = execute('SELECT id_category FROM categorys '
                                         'WHERE title_category = %(p)s',
                                         each_category)[0].get('id_category')  # находим новую категорию и записываем её
            execute('INSERT INTO podcasts_with_categorys(id_podcast, id_category) '
                    'VALUES (%(p)s, %(p)s)', id_new_podcast, id_new_category, commit=True)    # привязываем подкаст к этой категории
        else:
            id_category = execute('SELECT id_category FROM categorys WHERE title_category = %(p)s',
                                     each_category)[0].get('id_category')
            execute('INSERT INTO podcasts_with_categorys(id_category, id_podcast) VALUES (%(p)s, %(p)s)',
                    id_category, id_new_podcast, commit=True)

    for each_subcategory in subcat_podcast:   # добавляем подкатегории к подкасту
        if each_subcategory:   # во время срезки выходит пустая строка, доп проверка на неё
            execute('INSERT INTO subcat_podcast(id_podcast, title_subcat) VALUES (%(p)s, %(p)s)',
                    id_new_podcast, each_subcategory, commit=True)

    for each_keyword in keyword_podcast:  # тот же алгоритм что и с категориями
        if not each_keyword:
            break
        if not execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s', each_keyword):
            execute('INSERT INTO keywords (title_keyword) VALUES (%(p)s)', each_keyword, commit=True)
            id_new_keyword = execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s',
                                        each_keyword)[0].get('id_keyword')
            execute('INSERT INTO podcasts_with_keywords (id_podcast, id_keyword) VALUES (%(p)s, %(p)s)',
                    id_new_podcast, id_new_keyword, commit=True)
        else:
            id_keyword = execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s',
                                    each_keyword)[0].get('id_keyword')
            execute('INSERT INTO podcasts_with_keywords (id_podcast, id_keyword) VALUES (%(p)s, %(p)s)',
                    id_new_podcast, id_keyword, commit=True)


def check_item(title_item, title_podcast, audio):    # проверка на то , есть ли выпуск или нет
    if not execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast):
        return False
    id_podcast = execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast)[0].get('id_podcast')
    return execute('SELECT title_audio FROM items WHERE id_podcast = %(p)s AND '
                   'title_audio = %(p)s AND audio = %(p)s', id_podcast, title_item, audio)


def set_new_item(title_podcast, title_audio, description_audio, audio, image_audio, pubdata_audio,
                 duration_audio, category_item, subcategory_item, keyword_item):

    id_podcast = execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast)[0].get('id_podcast')
    if not duration_audio:
        duration_audio = None
    if not image_audio:
        image_audio = None
    if not pubdata_audio:
        pubdata_audio = None
    try:
        execute('INSERT INTO items (id_podcast, title_audio, description_audio, audio, image_audio, pubdata_audio, duration_audio)'
                ' VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', id_podcast, title_audio, description_audio, audio, image_audio,
                pubdata_audio, duration_audio, commit=True)
    except IndexError:
        print('Ошибка, не коммитит')
        return
    try:
        id_item = execute('SELECT id_item FROM items WHERE title_audio = %(p)s '
                             'AND id_podcast = %(p)s', title_audio, id_podcast)[0].get('id_item')
    except IndexError:
        print('Незакомитило')
        return

    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом
    for each_category in category_item:
        if not each_category:    # после обрезки, последний элемент - всегда пуст
            break
        else:
            execute('INSERT INTO cat_item(id_item, category) '
                    'VALUES (%(p)s, %(p)s)', id_item, each_category,
                    commit=True)  # привязываем подкаст к этой категории

    for each_subcategory in subcategory_item:
        if not each_subcategory:    # после обрезки, последний элемент - всегда пуст
            break
        else:
            execute('INSERT INTO subcat_item(id_item, title_subcategory) '
                    'VALUES (%(p)s, %(p)s)', id_item, each_subcategory,
                    commit=True)  # привязываем подкаст к этой категории

    for each_keyword in keyword_item:
        if not each_keyword:
            break
        if not execute('SELECT id_keyword_item FROM keywords_items WHERE title_keyword = %(p)s', each_keyword):
            execute('INSERT INTO keywords_items (title_keyword) VALUES (%(p)s)', each_keyword, commit=True)
            id_new_keyword = execute('SELECT id_keyword_item FROM keywords_items WHERE title_keyword = %(p)s',
                                        each_keyword)[0].get('id_keyword_item')
            execute('INSERT INTO items_with_keywords (id_item , id_keyword) VALUES (%(p)s, %(p)s)',
                    id_item, id_new_keyword, commit=True)
        else:
            id_keyword = execute('SELECT id_keyword_item FROM keywords_items WHERE title_keyword = %(p)s',
                                        each_keyword)[0].get('id_keyword_item')
            execute('INSERT INTO podcasts_with_keywords (id_podcast, id_keyword) VALUES (%(p)s, %(p)s)',
                    id_podcast, id_keyword, commit=True)


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
    execute('UPDATE url_podcasts SET url_podcast = %(p)s WHERE url_podcast = %(p)s',
            new_url, old_url, commit=True)


def add_url_in_error_links(url):
    """
        Добавляем url в таблицу error link, и удаляем её из основной
    """
    execute('DELETE FROM url_podcasts WHERE url_podcast = %(p)s', url, commit=True)
    execute('INSERT INTO error_links (url) VALUES (%(p)s)', url, commit=True)
