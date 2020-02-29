import util


def parse(url):
    util.execute('INSERT INTO url_podcasts (url_podcast, status_podcast) VALUES (%(p)s, %(p)s)', url, 1,
                 commit=True)  # ставим подкасту 0, что мы его уже скачали
#
# def parse(url):
#     util.execute('UPDATE url_podcasts SET status_podcast = 1 WHERE url_podcast = %(p)s', url,
#                  commit=True)  # ставим подкасту 0, что мы его уже скачали


if __name__ == '__main__':
    # util.execute('TRUNCATE categorys', commit=True)
    # util.execute('TRUNCATE items', commit=True)
    # util.execute('TRUNCATE items_with_keywords', commit=True)
    # util.execute('TRUNCATE keywords', commit=True)
    # util.execute('TRUNCATE keywords_items', commit=True)
    # util.execute('TRUNCATE podcasts', commit=True)
    # util.execute('TRUNCATE podcasts_with_categorys', commit=True)
    # util.execute('TRUNCATE podcasts_with_keywords', commit=True)
    # util.execute('TRUNCATE podcast_with_subcat', commit=True)
    # util.execute('TRUNCATE subcat_item', commit=True)
    # util.execute('TRUNCATE subcat_podcast', commit=True)
    # util.execute('TRUNCATE error_links', commit=True)
    # util.execute('TRUNCATE cat_item', commit=True)
    # util.execute('TRUNCATE url_podcasts', commit=True)
    # with open('parse_link.txt', 'r') as f:
    #     for i in enumerate(f.readlines()):
    #         if i[0] < 11:
    #             parse(i[1])
    # parse('https://podcasts.apple.com/ru/podcast/%D1%81%D0%B5%D1%80%D0%B3%D0%B5%D0%B9-%D1%81%D1%82%D0%B8%D0%BB%D0%BB%D0%B0%D0%B2%D0%B8%D0%BD-%D0%B8-%D0%B5%D0%B3%D0%BE-%D0%B4%D1%80%D1%83%D0%B7%D1%8C%D1%8F/id1207571791')
    # parse('http://spiridonov.ru/runetologia/rss_new/')
    # parse('https://ria.ru/export/iasdes/rss2/jeksponat.xml')
    # parse('https://aerostatica.ru/podcast.xml')
    # parse('https://feeds.simplecast.com/CPNlXNwD')
    # parse('https://rss.simplecast.com/podcasts/4464/rss')
    # parse('https://podster.fm/rss.xml?pid=20066')
    # parse('https://podster.fm/rss.xml?pid=29605')
    # parse('https://meduza.io/rss/podcasts/peremotka')
    # parse('https://mojomedia.ru/feed-podcasts/rebyata-my-potrahalis')
    # parse('http://feeds.feedburner.com/bizipodcast')
    # parse('https://anchor.fm/s/84ed588/podcast/rss')
    # parse('https://podster.fm/rss.xml?pid=40940')
    # parse('http://sharkov.podfm.ru/rss/rss.xml')
    # parse('https://feeds.fireside.fm/batinakonsol/rss')
    # parse('https://web-standards.ru/podcast/feed/')
    # parse('https://feeds.simplecast.com/hbz_rFz4')
    # parse('https://mojomedia.ru/feed-podcasts/dikie-utki')
    # parse('http://feeds.feedburner.com/DariaSadovaya')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:328939120/sounds.rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:132344904/sounds.rss')
    # parse('http://feeds.feedburner.com/pod24fps')
    # parse('https://anchor.fm/s/6f169f8/podcast/rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:679508342/sounds.rss')
    # parse('http://feeds.feedburner.com/americhka/oBlg')
    # parse('https://feeds.simplecast.com/TicU3npd')
    # parse('https://podster.fm/rss.xml?pid=42935')
    # parse('https://podster.fm/rss.xml?pid=62505')
    # parse('http://basicblockradio.libsyn.com/rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:542232678/sounds.rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:516686697/sounds.rss')
    # parse('https://feeds.simplecast.com/d1D4qHVy')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:569213187/sounds.rss')
    # parse('http://toinfinityandbeyond.libsyn.com/rss')
    # parse('https://warispeace.podigee.io/feed/mp3')
    # parse('http://feeds.feedburner.com/kommentator_podcast')
    # parse('https://echo.msk.ru/programs/garage/rss-audio.xml')
    # parse('https://pogovorim.stellav.ru/feed/podcast/')
    # parse('https://feeds.simplecast.com/o2q3_tiT')
    # parse('https://meduza.io/rss/podcasts/delo-sluchaya')
    # parse('https://anchor.fm/s/d6b7490/podcast/rss')
    # parse('https://podster.fm/rss.xml?pid=69579')
    # parse('https://pinecast.com/feed/designer')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:436210245/sounds.rss')
    # parse('http://feeds.soundcloud.com/users/soundcloud:users:602278230/sounds.rss')
    # parse('https://podster.fm/rss.xml?pid=35648')
    # parse('https://feeds.simplecast.com/v1cJ8X2Z')

