from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy, ugettext
import os
from ..downloading import DownloadServer, FsError


class WatchfolderDownloadServer(DownloadServer):
    def __init__(self, dirpath, **kwargs):
        if not os.path.isdir(dirpath):
            raise ImproperlyConfigured(
                "Created WatchfolderDownloadServer with " \
                "nonexisting dirpath '%s'." \
                % dirpath
            )
        self._dirpath = dirpath
        super(WatchfolderDownloadServer, self).__init__(**kwargs)

    def download_nzb_base(self, id, nzb, name=None):
        chunksize = 512 * 1024
        try:
            # get file in watchfolder for nzb
            f = None
            attempt = 1
            attempt_filename = id
            while f is None:
                f = open(os.path.join(
                    self._dirpath,
                    '%s.nzb' % attempt_filename,
                ), 'a')
                f.seek(0, os.SEEK_END)
                if f.tell() != 0:
                    # the file already exists!
                    f.close()
                    f = None
                    attempt += 1
                    attempt_filename = '%s (%s)' % (id, attempt)
            # we now have a nonexisting file opened
            # for writing (and seek() == 0)
            buf = nzb.read(chunksize)
            while buf:
                f.write(buf)
                buf = nzb.read(chunksize)
        except Exception as e:
            if f is not None:
                f.close()
            if isinstance(e, IOError):
                raise FsError(e.strerror)
            else:
                raise
        else:
            if name is None:
                return ugettext(u"Successfully placed nzb file in " \
                    "watchfolder, it was added under the name '%(id)s'.") \
                    % dict(id='%s.nzb' % attempt_filename)
            else:
                return ugettext(u"Successfully placed '%(name)s' in " \
                    "watchfolder, it was added under the name '%(id)s'.") \
                    % dict(name=name, id='%s.nzb' % attempt_filename)

    def download_nzb(self, user, id, nzb):
        return self.download_nzb_base(id, nzb)

    def download_spot(self, user, id, post):
        return self.download_nzb_base(id, post.get_nzb_file(), name=post.title)
