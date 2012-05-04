from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_noop as _
from load import load_object
from downloading import DownloadManager, DownloadServer



try:
    SERVER_HOST = settings.SPOTNET_SERVER_HOST
except AttributeError:
    raise ImproperlyConfigured("You haven't set the django-spotnet mandatory setting SPOTNET_SERVER_HOST.")

SERVER_PORT            = getattr(settings, 'SPOTNET_SERVER_PORT',            119)
SERVER_SSL             = getattr(settings, 'SPOTNET_SERVER_SSL',             False)
SERVER_USERNAME        = getattr(settings, 'SPOTNET_SERVER_USERNAME',        None)
SERVER_PASSWORD        = getattr(settings, 'SPOTNET_SERVER_PASSWORD',        None)
SERVER_READERMODE      = getattr(settings, 'SPOTNET_SERVER_READERMODE',      False)

UPDATE_MINPOST         = getattr(settings, 'SPOTNET_UPDATE_MINPOST',         None)
UPDATE_EXTRA           = getattr(settings, 'SPOTNET_UPDATE_EXTRA',         15000)
UPDATE_BULK_COUNT      = getattr(settings, 'SPOTNET_UPDATE_BULK_COUNT',      1000)
UPDATE_GROUPS          = getattr(settings, 'SPOTNET_UPDATE_GROUPS',          ('free.pt', 'spot.net', ))
UPDATE_COMMENT_GROUPS  = getattr(settings, 'SPOTNET_UPDATE_COMMENT_GROUPS',  ('free.usenet', ))
UPDATE_ALLOW_INPAGE    = getattr(settings, 'SPOTNET_UPDATE_ALLOW_INPAGE',    True)
UPDATE_LAST_STORAGE    = getattr(settings, 'SPOTNET_UPDATE_LAST_STORAGE',    False)
UPDATE_DISCARD_ENDINGS = getattr(settings, 'SPOTNET_UPDATE_DISCARD_ENDINGS', (SERVER_HOST,))

CLEANUP_MINAGE         = getattr(settings, 'SPOTNET_CLEANUP_MINAGE',         1999)
CLEANUP_ALLOW_INPAGE   = getattr(settings, 'SPOTNET_CLEANUP_ALLOW_INPAGE',   True)

POST_PER_PAGE          = getattr(settings, 'SPOTNET_POST_PER_PAGE',          30)
POST_LIST_ORPHANS      = getattr(settings, 'POST_LIST_ORPHANS',              POST_PER_PAGE//5)

ALLOW_NZB_UPLOAD       = getattr(settings, 'SPOTNET_ALLOW_NZB_UPLOAD',       True)

ANONYMOUS_ACTION       = getattr(settings, 'SPOTNET_ANONYMOUS_ACTION',       '404')

USE_CELERY             = getattr(settings, 'SPOTNET_USE_CELERY',             False)



# category settings

CATEGORY_MAPPING       = getattr(settings, 'SPOTNET_CATEGORY_MAPPING',     {
    1 : _('image'),
    2 : _('sound'),
    3 : _('game'),
    4 : _('application'),
})
CATEGORY_REVERSED_MAPPING = dict((v,k) for k,v in CATEGORY_MAPPING.iteritems())

SUBCATEGORY_TYPE_MAPPING = getattr(settings, 'SPOTNET_SUBCATEGORY_TYPE_MAPPING',     {
    1 : dict(
            a = _('format'),
            b = _('source'),
            c = _('language'),
            d = _('genre'),
            z = _('type'),
        ),
    2 : dict(
            a = _('format'),
            b = _('source'),
            c = _('bitrate'),
            d = _('genre'),
            z = _('type'),
        ),
    3 : dict(
            a = _('platform'),
            b = _('format'),
            c = _('genre'),
        ),
    4 : dict(
            a = _('platform'),
            b = _('genre'),
        ),
})

SUBCATEGORY_MAPPING = getattr(settings, 'SPOTNET_SUBCATEGORY_MAPPING',     {
    # source: https://github.com/spotweb/spotweb/blob/master/lib/SpotCategories.php
    1 : dict(
            format = {
                0 : _('DivX'),
                1 : _('wmv'),
                2 : _('mpg'),
                3 : _('dvd5'),
                4 : _('other highdef'),
                5 : _('ePub'),
                6 : _('Blu-ray'),
                7 : _('hd-dvd'),
                8 : _('wmvhd'),
                9 : _('x264hd'),
               10 : _('dvd9'),
            },
            source = {
                0 : _('cam'),
                1 : _('(s)vcd'),
                2 : _('promo'),
                3 : _('retail'),
                4 : _('tv'),
                #5 : _(''),
                6 : _('satellite'),
                7 : _('r5'),
                8 : _('telecine'),
                9 : _('telesync'),
               10 : _('scan'),
            },
            language = {
                0 : _('no subtitles'),
                1 : _('dutch subtitled (external)'),
                2 : _('dutch subtitled (internal)'),
                3 : _('english subtitled (external)'),
                4 : _('english subtitled (internal)'),
                #5 : _(''),
                6 : _('dutch subtitled (selectable)'),
                7 : _('english subtitled (selectable)'),
                #8 : _(''),
                #9 : _(''),
               10 : _('english spoken'),
               11 : _('dutch spoken'),
               12 : _('german spoken'),
               13 : _('french spoken'),
               14 : _('spanish spoken'),
            },
            genre = {
                0 : _('action'),
                1 : _('adventure'),
                2 : _('animation'),
                3 : _('cabaret'),
                4 : _('comedy'),
                5 : _('crime'),
                6 : _('documentary'),
                7 : _('drama'),
                8 : _('family'),
                9 : _('fantasy'),
               10 : _('art film'),
               11 : _('television'),
               12 : _('horror'),
               13 : _('music'),
               14 : _('musical'),
               15 : _('mystery'),
               16 : _('romance'),
               17 : _('science fiction'),
               18 : _('sport'),
               19 : _('short movie'),
               20 : _('thriller'),
               21 : _('war'),
               22 : _('western'),
               23 : _('erotica (hetero)'),
               24 : _('erotica (gay men)'),
               25 : _('erotica (gay women)'),
               26 : _('erotica (bi)'),
               #27 : _(''),
               28 : _('asian'),
               29 : _('anime'),
               30 : _('cover'),
               31 : _('comic'),
             '-32': _('cartoon'),    # DUPLICATE!
               32 : _('study'),
             '-33': _('kids'),       # DUPLICATE!
               33 : _('business'),
               34 : _('economics'),
               35 : _('computer'),
               36 : _('hobby'),
               37 : _('cooking'),
               38 : _('crafts'),
               39 : _('handwork'),
               40 : _('health'),
               41 : _('history'),
               42 : _('psychology'),
               43 : _('journal'),
               44 : _('magazine'),
               45 : _('science'),
               46 : _('women'),
               47 : _('religion'),
               48 : _('novel'),
               49 : _('biography'),
               50 : _('detective'),
               51 : _('animals'),
               52 : _('humor'),
               53 : _('travel'),
               54 : _('true events'),
               55 : _('nonfiction'),
               56 : _('politics'),
               57 : _('poetry'),
               58 : _('fairy tale'),
               59 : _('technics'),
               60 : _('art'),
               
               72 : _('bi'),
               73 : _('lesbian'),
               74 : _('gay'),
               75 : _('hetero'),
               76 : _('amature'),
               77 : _('group'),
               78 : _('pov'),
               79 : _('solo'),
               80 : _('young'),
               81 : _('soft'),
               82 : _('fetish'),
               83 : _('old'),
               84 : _('fat'),
               85 : _('sm'),
               86 : _('rough'),
               87 : _('dark'),
               88 : _('hentai'),
               89 : _('outside'),
            },
            type = {
                0 : _('movie'),
                1 : _('series'),
                2 : _('book'),
                3 : _('erotica'),
            },
        ),
    2 : dict(
            format = {
                0 : _('mp3'),
                1 : _('wma'),
                2 : _('wav'),
                3 : _('ogg'),
                4 : _('eac'),
                5 : _('dts'),
                6 : _('aac'),
                7 : _('ape'),
                8 : _('flac'),
            },
            source = {
                0 : _('cd'),
                1 : _('radio'),
                2 : _('compilation'),
                3 : _('dvd'),
                #4 : _(''),
                5 : _('vinyl'),
                6 : _('stream'),
            },
            bitrate = {
                0 : _('variable'),
                1 : _('< 96k'),
                2 : _('96k'),
                3 : _('128k'),
                4 : _('160k'),
                5 : _('192k'),
                6 : _('256k'),
                7 : _('320k'),
                8 : _('lossless'),
                #9 : _(''),
            },
            genre = {
                0 : _('blues'),
                1 : _('compilation'),
                2 : _('cabaret'),
                3 : _('dance'),
                4 : _('various'),
                5 : _('hardcore'),
                6 : _('world'),
                7 : _('jazz'),
                8 : _('kids'),
                9 : _('classic'),
               10 : _('preforming'),
               11 : _('dutch'),
               12 : _('new age'),
               13 : _('pop'),
               14 : _('r&b'),
               15 : _('hiphop'),
               16 : _('reggae'),
               17 : _('religious'),
               18 : _('rock'),
               19 : _('soundtrack'),
               #20 : _(''),
               21 : _('hardstyle'),
               22 : _('asian'),
               23 : _('disco'),
               24 : _('classics'),
               25 : _('metal'),
               26 : _('country'),
               27 : _('dubstep'),
               28 : _('dutch hiphop'),
               29 : _('drum&bass'),
               30 : _('electro'),
               31 : _('folk'),
               32 : _('soul'),
               33 : _('trance'),
               34 : _('balkan'),
               35 : _('techno'),
               36 : _('ambient'),
               37 : _('latin'),
               38 : _('live'),
            },
            type = {
                0 : _('album'),
                1 : _('liveset'),
                2 : _('podcast'),
                3 : _('audiobook'),
            },
        ),
    3 : dict(
            platform = {
                0 : _('windows'),
                1 : _('mac'),
                2 : _('unix'),
                3 : _('ps'),
                4 : _('ps2'),
                5 : _('psp'),
                6 : _('xbox'),
                7 : _('360'),
                8 : _('gba'),
                9 : _('gc'),
               10 : _('nds'),
               11 : _('Wii'),
               12 : _('ps3'),
               13 : _('windows phone'),
               14 : _('iOS'),
               15 : _('android'),
               16 : _('3ds'),
            },
            format = {
                0 : _('iso'),
                1 : _('rip'),
                2 : _('retail'),
                3 : _('dlc'),
                #4 : _(''),
                5 : _('patch'),
                6 : _('crack'),
            },
            genre = {
                0 : _('action'),
                1 : _('adventure'),
                2 : _('strategy'),
                3 : _('roleplay'),
                4 : _('simulation'),
                5 : _('race'),
                6 : _('flying'),
                7 : _('shooter'),
                8 : _('platform'),
                9 : _('sport'),
               10 : _('kids'),
               11 : _('puzzle'),
               #12 : _(''),
               13 : _('bordgame'),
               14 : _('cards'),
               15 : _('education'),
               16 : _('music'),
               17 : _('family'),
            },
        ),
    4 : dict(
            platform = {
                0 : _('windows'),
                1 : _('mac'),
                2 : _('unix'),
                3 : _('os/2'),
                4 : _('windows phone'),
                5 : _('nav'),
                6 : _('iOS'),
                7 : _('android'),
            },
            genre = {
                0 : _('audio'),
                1 : _('video'),
                2 : _('graphics'),
                3 : _('cd/dvd tools'),
                4 : _('media players'),
                5 : _('rippers & encoders'),
                6 : _('plugins'),
                7 : _('database tools'),
                8 : _('email software'),
                9 : _('picture managers'),
               10 : _('screensavers'),
               11 : _('skins'),
               12 : _('drivers'),
               13 : _('browsers'),
               14 : _('download managers'),
               15 : _('download'),
               16 : _('usenet software'),
               17 : _('rss readers'),
               18 : _('ftp software'),
               19 : _('firewalls'),
               20 : _('antivirus'),
               21 : _('antispyware'),
               22 : _('optimization software'),
               23 : _('security software'),
               24 : _('system software'),
               #25 : _(''),
               26 : _('educational'),
               27 : _('office'),
               28 : _('internet'),
               29 : _('communication'),
               30 : _('development'),
               31 : _('spotnet'),
            },
        ),
})



# spot verification keys

VERIFICATION_KEYS    = getattr(settings, 'SPOTNET_VERIFICATION_KEYS', (
    # default verification keys from: 
    '',
))



# download server settings and handling

DOWNLOAD_SERVERS = DownloadManager()

for server_name, server_settings in getattr(settings, 'SPOTNET_DOWNLOAD_SERVERS', {}).iteritems():
    server_type = load_object(server_settings[0])
    assert server_type is not None, "Spotnet download server '%s' at '%s' could not be found." % (server_name, server_settings[0])
    assert issubclass(server_type, DownloadServer), "Spotnet download server '%s' at '%s' is not a django-spotnet.DownloadServer subclass." % (server_name, server_settings[0])
    if len(server_settings) < 2:
        args = ()
    else:
        args = server_settings[1]
    if len(server_settings) < 3:
        kwargs = {}
    else:
        kwargs = server_settings[2]
    server = server_type(*args, **kwargs)
    DOWNLOAD_SERVERS.add_server(server_name, server)



