import urllib2
from django.utils.translation import ugettext_lazy, ugettext
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import settings


no_server_description_available_message = ugettext_lazy("No description given.")


class DownloadError(Exception):
    description = ugettext_lazy(u"An error occured while trying to download a post")

    def __init__(self, details=None):
        self.details = details

    def as_json_object(self):
        return dict()

    def as_json_object(self):
        obj = dict(
            description=self.description,
            type=type(self).__name__,
        )
        if self.details is not None:
            self.obj['details'] = self.details
        obj.update(self.as_json_object())
        return obj

    def as_message(self):
        ret = [
            ugettext(u'Downloading failed'),
            u':\n',
            ugettext(u'Description'),
            u':\n',
            self.description,
        ]
        if self.details is not None:
            ret.append(u'\n')
            ret.append(ugettext(u'Details'))
            ret.append(u':\n')
            ret.append(self.details)
        return u''.join(unicode(x) for x in ret)


class ConfigurationError(DownloadError):
    description = ugettext_lazy(u"An error in the configuration was detected")


class ConnectionError(DownloadError):
    description = ugettext_lazy(u"An error occured while connecting to the download server")


class PermissionDeniedError(DownloadError):
    description = ugettext_lazy(u"The requesting user was denied access to the download server")


class UnauthenticatedError(PermissionDeniedError):
    description = ugettext_lazy(u"The requesting user was denied access to the download server because he/she is unauthenticated")


class FsError(DownloadError):
    description = ugettext_lazy(u"There was an error when reading/writing the filesystem")


class DiskFullError(FsError):
    description = ugettext_lazy(u"Downloading failed because the disk is full")


class InvalidNzbError(DownloadError):
    description = ugettext_lazy(u"The nzb file is invalid")


class EmptyNzbError(InvalidNzbError):
    description = ugettext_lazy(u"The nzb file is an empty file")


class UnhandledDownloadError(DownloadError):
    description = ugettext_lazy(u"The DownloadServer instance failed to handle an exception")


def download_url(url, timeout):
    """Downloads a webpage.
    This is guaranteed to work, or throw an appropriate DownloadError.
    """
    try:
        response = urllib2.urlopen(url, None, timeout)
    except urllib2.HTTPError as e:
        raise ConnectionError(ugettext("While connecting to the server, " \
            "got an unexpected http response code: %s") % e.code)
    except urllib2.URLError as e:
        raise ConnectionError(ugettext("Error while connecting to the " \
            "server: %s") % e.reason)
    if response is None:
        raise ConnectionError(ugettext("While connecting to the server, " \
            "got nothing as response"))
    else:
        return response


class DownloadServer(object):
    def __init__(self, verbose_name=None, description=None, allow_anonymous=False, connection_timeout=None):
        self.verbose_name = verbose_name
        self.description = description
        self.allow_anonymous = allow_anonymous
        self._connection_timeout = 30 if connection_timeout is None else connection_timeout

    def download_post_base(self, user, id, post):
        if user.is_anonymous() and not self.allow_anonymous:
            raise UnauthenticatedError
        return self.download_post(user, id, post)

    def download_url_base(self, user, id, url):
        if user.is_anonymous() and not self.allow_anonymous:
            raise UnauthenticatedError
        return self.download_post(user, id, post)

    def download_nzb_base(self, user, id, nzb):
        if user.is_anonymous() and not self.allow_anonymous:
            raise UnauthenticatedError
        return self.download_nzb(user, id, nzb)

    def download_post(self, user, id, post):
        if getattr(self.download_nzb, 'implemented', True):
            return self.download_nzb(user, id, post.get_nzb_file())
        else:
            raise NotImplementedError("The download_post method of this " \
                "DownloadServer is not implemented.")

    def download_url(self, user, id, url):
        if getattr(self.download_nzb, 'implemented', True):
            # download the nzb at the url and add it directly
            response = download_url(url, self._connection_timeout)
            self.download_nzb(user, id, response)
        else:
            raise NotImplementedError("The download_url method of this " \
                "DownloadServer is not implemented.")
    download_url.implemented = False

    def download_nzb(self, user, id, post):
        raise NotImplementedError("The download_nzb method of this " \
            "DownloadServer is not implemented.")
    download_nzb.implemented = False


class DownloadManager(object):
    default_server_name = 'default'

    def __init__(self, servers={}):
        self._servers = dict(servers)

    def add_server(self, name, server):
        self._servers[name] = server

    def get_server(self, name):
        return self._servers.get(name, None)

    def has_servers(self):
        return len(self._servers) > 0

    def has_default(self):
        return self.default_server_name in self._servers

    def has_other_servers(self):
        "Returns true if there are any servers besides the default one"
        return len(self._servers) - int(self.default_server_name in self._servers) > 0

    def server_exists(self, name):
        return name in self._servers

    def get_default(self):
        if self.has_servers():
            return self.get_server(self.default_server_name)
        else:
            return None

    def get_server_verbose_name(self, server_name):
        server = self.get_server(server_name)
        if server.verbose_name:
            return server.verbose_name
        else:
            return server_name.capitalize()

    def get_server_description(self, server_name):
        server = self.get_server(server_name)
        if server.description:
            return server.description
        else:
            return no_server_description_avaiable_message

    def list_servers(self):
        return self._servers.keys()

    def list_servers_verbose(self):
        "This yields tuples of (server_name, server_verbose_name)"
        for server_name in self._servers:
            yield server_name, self.get_server_verbose_name(server_name)

    def list_servers_verbose_extensive(self):
        """This yields tuples of
        (server_name, server_verbose_name, server_description)
        """
        for server_name in self._servers:
            yield server_name, self.get_server_verbose_name(server_name)

    def download_post_base(self, post, server):
        """Download a post using a server.
        Post must be a Post instance,
        server must be a DownloadServer instance.
        This method is guarantied to either
        * return None
        * raise a DownloadError subclass as exception
        This is an internal method!
        """
        try:
            response = server.download_post(post)
        except DownloadError:
            raise
        except Exception as e:
            raise UnhandledDownloadError(e)
        else:
            return response

    def download_post(self, post, server_name=None):
        """This downloads a Post throug a named server.
        Returns None or raises a DownloadError subclass."""
        if server_name is None:
            server = self.get_default()
            assert server is not None, "Requested to download post from " \
                "default download server when there is no default defined."
        else:
            server = self.get_server(server_name)
            assert server is not None, "Requested to download post from " \
                "unknown download server '%s'." % server_name
        return server.download_post(post)


class PostDownload(object):
    def __init__(self, post):
        self.post = post

    def is_empty(self):
        return not settings.DOWNLOAD_SERVERS.has_servers()

    def has_default(self):
        return settings.DOWNLOAD_SERVERS.has_default()

    def has_others(self):
        return settings.DOWNLOAD_SERVERS.has_other_servers()

    def get_for_server(self, servername):
        return PostDownloadForServer(self.post, servername)

    def get_default(self):
        return self.get_for_server(settings.DOWNLOAD_SERVERS.default_server_name)

    def iter_others(self):
        for servername in settings.DOWNLOAD_SERVERS.list_servers():
            if not servername == settings.DOWNLOAD_SERVERS.default_server_name:
                yield self.get_for_server(servername)

    def __iter__(self):
        for servername in settings.DOWNLOAD_SERVERS.list_servers():
            yield self.get_for_server(servername)


class PostDownloadForServer(object):
    def __init__(self, post, servername):
        self.post = post
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
            kwargs=dict(
                id=self.post.id,
                dls=self.servername,
            ),
        )

    def is_default(self):
        return self.servername == settings.DOWNLOAD_SERVERS.default_server_name

    def render(self):
        description = self.description
        if description:
            return mark_safe(u'<a href="%s" title="%s">%s</a>' % \
                (self.url, description, conditional_escape(self.verbose_name)))
        else:
            return mark_safe(u'<a href="%s">%s</a>' % \
                (self.url, conditional_escape(self.verbose_name)))
