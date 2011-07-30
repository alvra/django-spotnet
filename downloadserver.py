from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy, ugettext
import os, json, urllib, urllib2
from downloading import DownloadServer, download_url \
    ConnectionError





class SabnzbdDownloadServer(DownloadServer):
    """Class for downloading through Sabnzbd.

    Sabnzbd api doc: http://wiki.sabnzbd.org/api
    """

    incorrect_api_response = 'error: API Key Incorrect'
    error_repsonse_start = 'error: '

    POST_PROCESSING = {
        0 : ugettext_lazy('Download'),
        1 : "+%s" % ugettext_lazy('Repair'),
        2 : "+%s" % ugettext_lazy('Unpack'),
        3 : "+%s" % ugettext_lazy('Delete'),
    }
    PRIORITY = {
       -1 : ugettext_lazy('Low'),
        0 : ugettext_lazy('Normal'),
        1 : ugettext_lazy('High'),
        2 : ugettext_lazy('Force'),
    }
    

    def __init__(self, 
      webpath, 
      apikey, 
      connection_timeout=10, 
      category=None, 
      priority=None, 
      finish_script=None, 
      post_processing=None, 
      **kwargs
    ):
        if not webpath.endswith('api'):
            raise ImproperlyConfigured("Created SabnzbdDownloadServer with invalid webpath '%s'." %  webpath)
        self._webpath = webpath
        self._apikey = apikey
        self._category = category
        self._priority = priority
        self._finish_script = finish_script
        self._post_processing = post_processing
        super(SabnzbdDownloadServer, self).__init__(**kwargs)

    def response_to_error(self, response):
        if response.read(len(self.incorrect_api_response)) == self.incorrect_api_response:
            raise ConfigurationError("Invalid Sabnzbd api key")
        elif response.read(len(self.error_repsonse_start)) == self.error_repsonse_start:
            raise DownloadError("Sabnzbd returned error while communicating: %s" % response.read()[error_repsonse_start:])
        else:
            raise DownloadError("Invalid Sabnzbd api key")

    def base_action(self, params):
        "Sends a message to sabnzbd server with param as message content dict"
        url = "%s?apikey=&s&output=json&%s" % (
            self._webpath,
            self._apikey,
            urllib.urlencode(params.iteritems()),
        )

        response = download_url(url, self._connection_timeout)

        try:
            ret = json.JSONDecoder().decode(response)
        except ValueError:
            return self.response_to_error(response)

        if ret['status'] is False:
            raise DownloadError(ret['error'])
        else:
            return ret


    def base_download_params(self, user):
        params = {}
        if self._category is not None:
            params['cat'] = self._category
        if self._post_processing is not None:
            params['pp'] = self._post_processing
        if self._finish_script is not None:
            params['script'] = self._finish_script
        if self._priority is not None:
            params['priority'] = self._priority


    def download_nzb(self, user, id, nzb):
        temppath = os.tempname()
        chunksize = 512 * 1024
        with open(temppath, 'w') as f:
            buf = nzb.read(chunksize)
            while buf:
                f.write(buf)
                buf = nzb.read(chunksize)
        return download_local_nzb(user, id, temppath)

    def download_local_nzb(self, user, id, path):
        x = self.base_action(dict(
            mode = 'addlocalfile',
            name = path,
            nzbname = id,
        ))
        if x['status'] is True:
            return ugettext(u"Successfully added url '%(url)s' to Sabnzbd server, it was added under the name '%(id)s'.") % dict(url=url,id=id)
        else:
            raise DownloadError(ugettext("An unknown error occured, response was: %s") % x)

    def download_url(self, user, id, url):
        x = self.base_action(dict(
            mode = 'addurl',
            name = url,
            nzbname = id,
        ))
        if x['status'] is True:
            return ugettext(u"Successfully added url '%(url)s' to Sabnzbd server, it was added under the name '%(id)s'.") % dict(url=url,id=id)
        else:
            raise DownloadError(ugettext("An unknown error occured, response was: %s") % x)





class WatchfolderDownloadServer(DownloadServer):
    def __init__(self, dirpath, **kwargs):
        if not os.path.isdir(dirpath):
            raise ImproperlyConfigured("Created WatchfolderDownloadServer with nonexisting dirpath '%s'." %  dirpath)
        self._dirpath = dirpath
        super(WatchfolderDownloadServer, self).__init__(**kwargs)

    def download_nzb(self, user, id, post):
        temppath = os.tempname(self._dirpath)
        chunksize = 512 * 1024
        with open(temppath, 'w') as f:
            buf = nzb.read(chunksize)
            while buf:
                f.write(buf)
                buf = nzb.read(chunksize)
        return download_local_nzb(user, id, temppath)





