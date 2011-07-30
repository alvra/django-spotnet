from time import sleep
from django.conf import settings
from django.db.models import Max
from django.db import IntegrityError
from pySpotnet.nntplib import NNTP
from pySpotnet.SpotFetcher import SpotFetcher

from models import SpotnetPost
import downloadserver





#
# EXTENSIVE TODO'S:
# * pevent multiple simultanious updates
# * allow omitting some of the settings in the settings file
#





DEFAULT_DOWNLOADSERVER_NAME = 'default'
NEWSSERVER_UNAUTH_USERNAME = None
NEWSSERVER_UNAUTH_PASSWORD = None
DBITEMS_ITERATE_SLEEPTIME = 0   # TODO: determine optimal sleeptime to avoid stressing the db





# utility functions

def get_newsserver():
    return NNTP(
        host = settings.SPOTNET_SERVER_HOST,
        port = settings.SPOTNET_SERVER_PORT,
        user = settings.SPOTNET_SERVER_USERNAME or NEWSSERVER_UNAUTH_USERNAME,
        password = settings.SPOTNET_SERVER_PASSWORD or NEWSSERVER_UNAUTH_PASSWORD,
    )

def get_max_stored_spotid():
    "Returns an integer indicating the maximum known post id in the db, or None if no posts found"
    try:
        max_spotid = SpotnetPost.objects.aggregate(m=Max('spotid'))['m']   # TODO: is this correct?
    except:
        return None
    else:
        assert isinstance(max_spotid, (int,long)) or max_spotid is None   # DEBUG
        return max_spotid

def spotid_is_stored(spotid):
    return SpotnetPost.objects.filter(spotid=spotid).count() == 0

def import_path(path):
    "Imports returns the python object specified by the import path, or raises ImportError"
    raise NotImplementedError

def get_downloadserver(name=None):
    if not name:
        name = DEFAULT_DOWNLOADSERVER_NAME
    params = settings.SPOTNET_DOWNLOAD_SERVERS.get(name, None)
    if not params:
        raise Exception("Value for SPOTNET_DOWNLOAD_SERVERS server named '%s' is empty" % name)
    elif isinstance(params, downloadserver.DownloadServer):
        return params
    elif isinstance(params, tuple):
        try:
            dls_class = import_path(params[0])
        except ImportError as e:
            raise Exception("Path to server class for SPOTNET_DOWNLOAD_SERVERS server named '%s' could not be imported, error was:\n%s" % (name,e))
    else:
        raise TypeError("Value for SPOTNET_DOWNLOAD_SERVERS server named '%s' is of invalid type" % name)
    



# application functions

def add_spot(spot):
    "Adds a pySpotnet.Spot instance to the db."
    # TODO: catch errors for dupliaction of the unique keys (happens!)
    try:
        snp = SpotnetPost.from_spot(spot)
        snp.save()
        return snp
    except IntegrityError:   # probably duplicate entry (for key 'messageid_index')
        return None

def try_add_spot_by_id(spotid, newsserver=None):
    "Tries to add spot with given id, returns True on success."
    if newsserver is None:
        newsserver = get_newsserver()
    spot_fetcher = SpotFetcher(newsserver)
    try:
        spot = spot_fetcher(spotid)
    except:   # TODO: insert expected base exception
        return False
    add_spot(spot)
    return True

def update(thorough=False):
    "Adds new spots to the db, the amount added is returned."
    if thorough:
        return update_thorough(newsserver=get_newsserver())
    else:
        return update_sloppy(newsserver=get_newsserver())

def update_sloppy(newsserver=None):
    if newsserver is None:
        newsserver = get_newsserver()
    #min_spotid = settings.SPOTNET_UPDATE_MINPOST
    min_spotid = get_max_stored_spotid()
    if min_spotid is None:
        min_spotid = settings.SPOTNET_UPDATE_MINPOST
    else:
        min_spotid += 1

    spot_fetcher = SpotFetcher(newsserver)
    spots_added = 0
    #for h in spot_fetcher.get_spot_headers(min_spotid, None):
    for h in spot_fetcher.get_spot_headers(1, 200000000):
    #for h in spot_fetcher.get_spot_headers(1, 100000):
        try:
            spot = spot_fetcher.get_spot(h.message_id)
        except:   # TODO: insert expected base exception
            pass
        else:
            if spot is not None:
                add_spot(spot)
                spots_added += 1
                sleep(DBITEMS_ITERATE_SLEEPTIME)
    return spots_added

def update_thorough(newsserver=None):
    if newsserver is None:
        newsserver = get_newsserver()
    min_spotid = settings.SPOTNET_UPDATE_MINPOST
    max_iterate_spotid = get_max_stored_spotid()
    spots_added = 0
    # TODO: what happens when we aggregate an empty query?
    for n in xrange(min_spotid, max_iterate_spotid):
        if not spotid_is_stored(n):
            if try_add_spot_by_id(n):
                spots_added += 1
        sleep(DBITEMS_ITERATE_SLEEPTIME)
    # the ones we don't yet have can be added sloppily
    return spots_added + update_sloppy(newsserver)
        
        
        



def cleanup():
    minage = settings.SPOTNET_CLEANUP_MINAGE
    SpotnetPost.objects.filter(timestamp_lt=minage*86400).delete()



def download_snpid(pk, servername=None):
    """Downloads a SpotnetPost instance (specified by pk) using the specified or default download server.
    All exceptions are subclass of DownloadError.
    """
    try:
        return download_snp(SpotnetPost.objects.get(pk=pk))
    except SpotnetPost.DoesNotExist:
        raise   # TODO: maybe make this into a better exception?



def download_snp(snp, servername=None):
    """Downloads a SpotnetPost instance using the specified or default download server.
    All exceptions are subclass of DownloadError.
    """
    dls = get_downloadserver(name)
    dls.download_spot(snp)



def download_nzb_location(nzb_location, servername=None):
    """Downloads a nzb (given fs path to the nzb file) using the specified or default download server.
    All exceptions are subclass of DownloadError.
    """
    try:
        f = open(nzb_location, 'r')
    except IOError as e:
        raise downloadserver.exceptions.FileError("%s : %s" % (e.__doc__, e.strerror))   # TODO: maybe make this into a better exception?
    # now we have the file, download it
    try:
        return download_nzb(f)
    except Exception:
        f.close()
        raise



def download_nzb(nzb, servername=None):
    """Downloads a nzb (given a file like object) using the specified or default download server.
    All exceptions are subclass of DownloadError.
    """
    dls = get_downloadserver(name)
    dls.download_nzb(nzb)



