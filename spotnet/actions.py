import os
import zipfile
import mimetypes
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.translation import ugettext as _
from django.contrib import messages
from models import Post, PostDownloaded
from connection import Connection, NotFoundError


class Action(object):
    "Base class for all actions"

    def apply(self, request, objects):
        raise NotImplementedError("The 'apply' method of this Action is not implemented")

    def title(self):
        raise NotImplementedError("The 'apply' method of this Action is not implemented")


class DeleteAction(object):
    "Action to delete database objects"

    def __init__(self, model, title=None):
        self._model = model
        self._title = title

    def apply(self, request, pks):
        objects = self._model.objects.filter(pk__in=pks)
        objects.delete()

    def title(self):
        return self._title or _('Delete')


class DownloadFileAction(Action):
    "Base action to download files"

    # private methods

    def get_temp_file(self):
        return os.tmpfile()

    def clean_response_header(self, x):
        """Clean strings for response headers
        These need to be encoded in us-ascii,
        which does not allow characters above 127
        """
        if isinstance(x, unicode):
            return x.encode('us-ascii', 'replace')
        else:
            # just assume it is already encoded in us-ascii
            return x

    def get_path_mimetype(self, filepath):
        return mimetypes.guess_type(filepath)

    def get_path_filesize(self, filepath):
        return os.path.getsize(filepath)

    def base_download_zip(self, z, name):
        return self.base_download(z, name, mimetype='application/zip')

    def base_download(self, f, name, filepath=None, mimetype=None, filesize=None):
        if mimetype is None:
            if filepath is None:
                raise ValueError
            else:
                mimetype = self.get_path_mimetype(filepath)
        if filesize is None:
            if filepath is None:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0)
            else:
                filesize = self.get_path_filesize(filepath)
        response = HttpResponse(FileWrapper(f), mimetype=mimetype)
        response['Content-Disposition'] = self.clean_response_header( \
            u'attachment; filename=%s' % name)
        response['Content-Length'] = self.clean_response_header(unicode(filesize))
        return response

    # public methods (name is the proposed filename to the client browser)

    def download_filepath(self, f, name, mimetype=None):
        "Download a file by giving it's path"
        return self.base_download(f, name, filepath=f, mimetype=mimetype)

    def download_file(self, f, name, mimetype=None, filesize=None):
        "Download a file by giving a file like object"
        return self.base_download(
            f,
            name,
            mimetype=mimetype,
            filesize=filesize,
        )

    def download_several_filepaths(self, files, name):
        "Download a file by giving a dict of names to filepaths"
        tempfile = self.get_temp_file()
        z = zipfile.ZipFile(tempfile, 'w')
        for filename, filepath in files.iteritems():
            z.write(filepath, filename)
        z.close()
        return self.base_download_zip(tempfile, name)

    def download_several_files(self, files, name):
        "Download a file by giving a dict of names to files"
        tempfile = self.get_temp_file()
        z = zipfile.ZipFile(tempfile, 'w')
        for filename, fil in files.iteritems():
            z.writestr(filename, fil.read())
        z.close()
        return self.base_download_zip(tempfile, name)


class DownloadNzbAction(DownloadFileAction):
    "Action to download nzb files from Posts"

    nzb_mimetype = 'application/x-nzb'

    def title(self):
        return _('Download nzb files')

    def post_to_filename(self, post):
        return '%s.nzb' % post.title

    def get_post_from_single_pk(self, pk):
        return Post.objects.get(pk=pk)

    def get_posts_from_several_pks(self, pks):
        return Post.objects.filter(pk__in=pks)

    def mark_posts_downloaded(self, user, posts):
        if isinstance(posts, Post):
            posts.mark_downloaded(user)
        else:
            for post in posts:
                post.mark_downloaded(user)

    def get_nzb(self, request, post, connection=None):
        try:
            return post.get_nzb_file(connection=connection)
        except NotFoundError:
            messages.warning(request, _("Could not download nzb for '%s' " \
                "since it does not exist on the server anymore.") % post.title)
            return None

    def apply(self, request, pks):
        if len(pks) == 0:
            messages.warning(request, _("Could not download nzbs since no " \
                "posts were selected."))
            return None
        else:
            posts = self.get_posts_from_several_pks(pks)
            if len(posts) == 0:
                messages.warning(request, _("The posts you requested to " \
                    "download nzbs from do not exist."))
                return None
            if len(pks) != len(posts):
                messages.error(request, _("Some of the posts you requested " \
                    "to download nzbs from do not exist."))
            if len(posts) == 1:
                self.mark_posts_downloaded(request.user, posts[0])
                nzb = self.get_nzb(request, posts[0])
                if nzb:
                    return self.download_file(
                        nzb,
                        self.post_to_filename(posts[0]),
                        mimetype=self.nzb_mimetype,
                    )
                else:
                    return None
            else:
                if len(posts) != len(pks):
                    messages.error(request, _("Could not download all nzbs " \
                        "for all posts you requested since some of them " \
                        "do not exists."))
                self.mark_posts_downloaded(request.user, posts)
                connection = Connection(connect=True)

                files = [(
                    self.post_to_filename(post),
                    self.get_nzb(request, post, connection)
                ) for post in posts]
                files = [f for f in files if f[1] is not None]
                if files:
                    return self.download_several_files(
                        dict(files),
                        'nzb (%s).zip' % len(posts),
                    )
                else:
                    return None


class DownloadRelatedNzbAction(DownloadNzbAction):
    """Action to download nzb files from database objects
    that have a foreignkey to a Post named 'post'
    """

    def get_post_from_single_pk(self, pk):
        raise NotImplementedError

    def get_posts_from_several_pks(self, pks):
        raise NotImplementedError
