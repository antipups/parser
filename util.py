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


def set_new_podcast(title_of_podcast, description_of_podcasts, url_of_image_of_podcast, author_of_podcast, tags_of_podcast):
    print(tags_of_podcast)
    # execute('INSERT INTO podcasts (title_of_podcast, description_of_podcast, url_of_image_of_podcast, author_of_podcast) '
    #         'VALUES (%(p)s, %(p)s, %(p)s, %(p)s)', title_of_podcast, description_of_podcasts, url_of_image_of_podcast, author_of_podcast,
    #         commit=True)
    # id_of_podcast = execute('SELECT id_of_podcasts FROM podcasts WHERE title_of_podcast = "(%(p)s)"', title_of_podcast)[0].get('title_of_podcast')
    # execute('INSERT INTO tags_of_podcasts () VALUES (%(p)s, %(p)s)', id_of_podcast,
    #         commit=True)


def set_new_item(title_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio, pubdata_of_audio, duration_of_audio):
    id_of_podcast = execute('SELECT id_of_podcast FROM podcasts WHERE title_of_podcast = %(p)s', title_of_podcast)[0].get('id_of_podcast')
    execute('INSERT INTO audio (id_of_podcast, titile_of_audio, description_of_audio, audio, image_of_audio, pubdata_of_audio, duration_of_audio)'
            ' VALUES (%(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s, %(p)s)', id_of_podcast, title_of_audio, description_of_audio, audio, image_of_audio,
            pubdata_of_audio, duration_of_audio, commit=True)
