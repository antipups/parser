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

    # получаем id нового подкаста для скачки тегов и категорий
    id_new_podcast = execute('SELECT id FROM url_podcasts WHERE url_podcast = %(p)s',
                             url_podcast)[0].get('id')

    execute('INSERT INTO podcasts (title_podcast, description_podcast, url_image_podcast, author_podcast, id_podcast) '  # добавляем новый подкаст
            'VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', title_podcast, description_podcasts, url_image_podcast, author_podcast, id_new_podcast,
            commit=True)

    # проходимся по всем категориям, если такой нет записываем в категории, и соединяем с подкастом, иначе просто соединяем с подкастом
    for each_category in category_podcast[:-1]:
        if not execute('SELECT id_category FROM categorys WHERE title_category = %(p)s', each_category):
            execute('INSERT INTO categorys(title_category) VALUES (%(p)s)', each_category, commit=True)   # если нет такой категории, создаем
            id_category = execute('SELECT id_category FROM categorys '
                                  'WHERE title_category = %(p)s',
                                   each_category)[0].get('id_category')  # находим новую категорию и записываем её
        else:
            id_category = execute('SELECT id_category FROM categorys WHERE title_category = %(p)s',
                                     each_category)[0].get('id_category')

        if not execute('SELECT * FROM podcasts_with_categorys WHERE id_podcast = %(p)s AND id_category = %(p)s',    # если данной связки ещё нет
                       id_new_podcast, id_category):

            execute('INSERT INTO podcasts_with_categorys(id_category, id_podcast) VALUES (%(p)s, %(p)s)',
                    id_category, id_new_podcast, commit=True)

    for each_subcategory in subcat_podcast:   # добавляем подкатегории к подкасту
        if each_subcategory:   # во время срезки выходит пустая строка, доп проверка на неё
            if not execute('SELECT * FROM subcat_podcast WHERE title_subcat = (%(p)s)', each_subcategory):
                execute('INSERT INTO subcat_podcast (title_subcat) VALUES (%(p)s)', each_subcategory, commit=True)
            id_subcat = execute('SELECT id_subcat FROM subcat_podcast WHERE title_subcat = (%(p)s)', each_subcategory)[0].get('id_subcat')
            execute('INSERT INTO podcast_with_subcat(id_podcast, id_subcat) VALUES (%(p)s, %(p)s)',
                    id_new_podcast, id_subcat, commit=True)



    for each_keyword in keyword_podcast[:-1]:  # тот же алгоритм что и с категориями
        if not execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s', each_keyword):

            execute('INSERT INTO keywords (title_keyword) VALUES (%(p)s)', each_keyword, commit=True)
            id_keyword = execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s',
                                        each_keyword)[0].get('id_keyword')
        else:
            id_keyword = execute('SELECT id_keyword FROM keywords WHERE title_keyword = %(p)s',
                                    each_keyword)[0].get('id_keyword')

        if not execute('SELECT * FROM podcasts_with_keywords WHERE id_podcast = %(p)s AND id_keyword = %(p)s',
                       id_new_podcast, id_keyword):
            execute('INSERT INTO podcasts_with_keywords (id_podcast, id_keyword) VALUES (%(p)s, %(p)s)',
                    id_new_podcast, id_keyword, commit=True)


def check_item(title_item, title_podcast, audio):    # проверка на то , есть ли выпуск или нет
    if not execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast):
        return False
    id_podcast = execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast)[0].get('id_podcast')
    return bool(execute('SELECT title_audio FROM items WHERE id_podcast = %(p)s AND '
                        'title_audio = %(p)s AND audio = %(p)s', id_podcast, title_item, audio))


def set_new_item(title_podcast, title_audio, description_audio, audio, image_audio, pubdata_audio,
                 duration_audio, category_item, subcategory_item, keyword_item):

    id_podcast = execute('SELECT id_podcast FROM podcasts WHERE title_podcast = %(p)s', title_podcast)[0].get('id_podcast')
    if not duration_audio:  # if детектит пустую строку, а None - нет
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

    id_item = execute('SELECT id_item FROM items WHERE title_audio = %(p)s '
                      'AND id_podcast = %(p)s', title_audio, id_podcast)[0].get('id_item')

    for each_category in category_item[:-1]:
        execute('INSERT INTO cat_item(id_item, title_category) '
                'VALUES (%(p)s, %(p)s)', id_item, each_category,
                commit=True)

    for each_subcategory in subcategory_item[:-1]:
        execute('INSERT INTO subcat_item(id_item, title_subcategory) '
                'VALUES (%(p)s, %(p)s)', id_item, each_subcategory,
                commit=True)

    for each_keyword in keyword_item[:-1]:
        if not execute('SELECT id_keyword_item FROM keywords_items WHERE title_keyword = %(p)s', each_keyword):
            execute('INSERT INTO keywords_items (title_keyword) VALUES (%(p)s)', each_keyword, commit=True)
            id_keyword = execute('SELECT id_keyword_item FROM keywords_items WHERE title_keyword = %(p)s',
                                        each_keyword)[0].get('id_keyword_item')
        else:
            id_keyword = execute('SELECT id_keyword_item FROM keywords_items WHERE title_keyword = %(p)s',
                                        each_keyword)[0].get('id_keyword_item')
        execute('INSERT INTO items_with_keywords (id_item, id_keyword) VALUES (%(p)s, %(p)s)',
                id_item, id_keyword, commit=True)


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


def add_url_in_error_links(url):
    """
        Добавляем url в таблицу error link, и удаляем её из основной
    """
    execute('DELETE FROM url_podcasts WHERE url_podcast = %(p)s', url, commit=True)
    if not execute('SELECT * FROM error_links WHERE (%(p)s)', url):
        execute('INSERT INTO error_links (url) VALUES (%(p)s)', url, commit=True)
