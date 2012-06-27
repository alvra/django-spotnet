from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy, ugettext
import os
import json
import urllib
from ..downloading import DownloadServer, download_url, \
    DownloadError, \
    ConnectionError, \
    ConfigurationError


class NzbgetDownloadServer(DownloadServer):
    """Class for downloading through NZBGet.

    NZBGet api doc: http://nzbget.sourceforge.net/RPC_API_reference
    """

    def __init__(
            self,
            webpath,
            **kwargs):
        self._webpath = webpath
        raise NotImplementedError  # TODO: implement this
        super(NzbgetDownloadServer, self).__init__(**kwargs)
