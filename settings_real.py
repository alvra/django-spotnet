from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from load import load_object
from downloading import DownloadManager, DownloadServer



try:
    SERVER_HOST = settings.SPOTNET_SERVER_HOST
except AttributeError:
    raise ImproperlyConfigured("You haven't set the django-spotnet mandatory setting SPOTNET_SERVER_HOST.")

SERVER_PORT          = getattr(settings, 'SPOTNET_SERVER_PORT',          119)
SERVER_SSL           = getattr(settings, 'SPOTNET_SERVER_SSL',           False)
SERVER_USERNAME      = getattr(settings, 'SPOTNET_SERVER_USERNAME',      None)
SERVER_PASSWORD      = getattr(settings, 'SPOTNET_SERVER_PASSWORD',      None)
SERVER_READERMODE    = getattr(settings, 'SPOTNET_SERVER_READERMODE',    False)

UPDATE_MINPOST       = getattr(settings, 'SPOTNET_UPDATE_MINPOST',       None)
UPDATE_BULK_COUNT    = getattr(settings, 'SPOTNET_UPDATE_BULK_COUNT',    20)
UPDATE_GROUPS        = getattr(settings, 'SPOTNET_UPDATE_GROUPS',        ('free.pt',))
UPDATE_ALLOW_INPAGE  = getattr(settings, 'SPOTNET_UPDATE_ALLOW_INPAGE',  True)

CLEANUP_MINAGE       = getattr(settings, 'SPOTNET_CLEANUP_MINAGE',       1999)
CLEANUP_ALLOW_INPAGE = getattr(settings, 'SPOTNET_CLEANUP_ALLOW_INPAGE', True)

POST_PER_PAGE        = getattr(settings, 'SPOTNET_POST_PER_PAGE',        20)

ALLOW_NZB_UPLOAD     = getattr(settings, 'SPOTNET_ALLOW_NZB_UPLOAD',     True)

ANONYMOUS_ACTION     = getattr(settings, 'SPOTNET_ANONYMOUS_ACTION',     '404')

USE_CELERY           = getattr(settings, 'SPOTNET_USE_CELERY',           False)

VERIFICATION_KEYS    = getattr(settings, 'SPOTNET_VERIFICATION_KEYS', (
    # default verification keys from: 
    '',
))



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



