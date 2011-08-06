from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import settings





class SpotDownload(object):
    def __init__(self, spot):
        self.spot = spot

    def is_empty(self):
        return not settings.DOWNLOAD_SERVERS.has_servers()

    def has_default(self):
        return settings.DOWNLOAD_SERVERS.has_default()

    def has_others(self):
        return settings.DOWNLOAD_SERVERS.has_other_servers()

    def get_for_server(self, servername):
        return SpotDownloadForServer(self.spot, servername)


    def get_default(self):
        return self.get_for_server(settings.DOWNLOAD_SERVERS.default_server_name)

    def iter_others(self):
        for servername in settings.DOWNLOAD_SERVERS.list_servers():
            if not servername == settings.DOWNLOAD_SERVERS.default_server_name:
                yield self.get_for_server(servername)

    def __iter__(self):
        for servername in settings.DOWNLOAD_SERVERS.list_servers():
            yield self.get_for_server(servername)





class SpotDownloadForServer(object):
    def __init__(self, spot, servername):
        self.spot = spot
        self.servername = servername

    @property
    def name(self):
        return self.servername

    @property
    def verbose_name(self):
        return settings.DOWNLOAD_SERVERS.get_server_verbose_name(self.servername)

    @property
    def description(self):
        return settings.DOWNLOAD_SERVERS.get_server_description(self.servername)

    @property
    def url(self):
        return reverse(
            'spotnet:download_using', 
            kwargs = dict(
                id = self.spot.id, 
                dls = self.servername,
            ),
        )

    def is_default(self):
        return self.servername == settings.DOWNLOAD_SERVERS.default_server_name

    def render(self):
        description = self.description
        if description:
            return mark_safe(u'<a href="%s" title="%s">%s</a>' % (self.url, description, conditional_escape(self.verbose_name)))
        else:
            return mark_safe(u'<a href="%s">%s</a>' % (self.url, conditional_escape(self.verbose_name)))





