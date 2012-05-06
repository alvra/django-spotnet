import nntplib, socket, errno, os, sys
import settings
import zlib
from cStringIO import StringIO
from django.db import IntegrityError
from models import Post, PostMarker
from post import RawPost, InvalidPost



# TODO:
# maybe decode headers using a function (new in python 3?)
# http://docs.python.org/py3k/library/nntplib.html?highlight=nntp#nntplib.decode_header

noop = lambda x: None





NEWSSERVER_UNAUTH_USERNAME = None
NEWSSERVER_UNAUTH_PASSWORD = None





class ConnectionError(Exception):
    pass
class ConnectError(ConnectionError):
    pass



#
# We are working with two types of id's here
#
# - messageid : universally unique id, eg: '<3ae6b2dcccdf42988a85dc314370ba0123@free.pt>'
# - postnumber : server dependent id, eg: '65903' (always use strings in nntplib!)
#

class Connection(object):
    """Class to connect to the nntp server with."""

    def __init__(self, connect=True):
        self._nntp = None
        if connect:
            self.connect()



    # public methods

    def is_connected(self):
        return self._nntp is not None

    def connect(self):
        # connect to server
        try:
            if sys.version[:2] < (3,2):
                nntp = nntplib.NNTP(
                    host = settings.SERVER_HOST,
                    port = settings.SERVER_PORT,
                    user = settings.SERVER_USERNAME \
                        if settings.SERVER_USERNAME is not None \
                        else NEWSSERVER_UNAUTH_USERNAME,
                    password = settings.SERVER_PASSWORD\
                        if settings.SERVER_PASSWORD is not None \
                        else NEWSSERVER_UNAUTH_PASSWORD,
                    readermode = settings.SERVER_READERMODE,
                    usenetrc = False,
                )
            else:
                # try to encrypt connection using ssl
                nntp = nntplib.NNTP(
                    host = settings.SERVER_HOST,
                    port = settings.SERVER_PORT,
                    readermode = settings.SERVER_READERMODE,
                    usenetrc = False,
                )
                nntp.starttls(ssl_context=None) # this method is introduced in python 3.2
                # login, now that we might be encrypted
                nntp.login(
                    user = settings.SERVER_USERNAME if settings.SERVER_USERNAME is not None else NEWSSERVER_UNAUTH_USERNAME,
                    password = settings.SERVER_PASSWORD if settings.SERVER_PASSWORD is not None else NEWSSERVER_UNAUTH_PASSWORD,
                )
        except (nntplib.NNTPError, socket.error) as e:
            raise ConnectError(e)
        self._nntp = nntp

    def disconnect(self):
        if self.is_connected():
            try:
                quitmsg = self._nntp.quit()
            except EOFError:
                # seems to happen for me, but we're still disconnected
                # TODO: find a way to check if we're really disconnected
                # and rethrow the exception if not
                pass
            self._nntp = None

    def update(self, logger=noop):
        "Retrieves all new posts."
        logger("Updating spotnet")
        for group in settings.UPDATE_GROUPS:
            self.update_group(group, logger=lambda x: logger('  %s'%x))



    # private update methods

    def update_group(self, groupname, logger=noop):
        logger("Updating group '%s'" % groupname)
        try:
            gresp = self._nntp.group(groupname)
        except (nntplib.NNTPError, socket.error) as e:
            logger("Failed updating group '%s': %s" % (groupname,e))
            return ConnectionError(e)

        first_on_server,last = gresp[2],gresp[3] # first < last
        last_in_db = self.get_last_postnumber_in_db()

        first_options = [int(first_on_server)]
        if last_in_db is not None:
            first_options.append(int(last_in_db))
        if settings.UPDATE_MINPOST is not None:
            first_options.append(settings.UPDATE_MINPOST)
        first = max(first_options)

        last = int(last)
        curstart = first
        last_added = None
        while curstart < last + settings.UPDATE_EXTRA:
            x = self.update_group_postnumbers(
                groupname,
                curstart,
                curstart+settings.UPDATE_BULK_COUNT,
                logger = lambda x: logger('  %s'%x),
            )
            if x:
                last_added = x
            curstart += settings.UPDATE_BULK_COUNT

        # store last added post's postnumber
        # since there's not always a way to obtain it
        # from the last messageid alone
        if settings.UPDATE_LAST_STORAGE:
            self.set_last_postnumber_in_db(last_added)

    def update_group_postnumbers(self, groupname, start, end, logger=noop):
        logger("Updating group '%s', block [%d, %d]" % (groupname,start,end))
        try:
            xover = self._nntp.xover(str(start), str(end))
        except (nntplib.NNTPError, socket.error) as e:
            logger("Error updating group '%s', block [%d, %d]: %s" % (groupname,start,end,e))
            raise ConnectionError(e)
        last_added = None
        index = 0
        while index < len(xover[1]):
            post = xover[1][index]
            # we limit ourselves here since not all posts
            # seem to provide real spotnet posts
            if post[4][:-1].split('@',1)[-1] not in settings.UPDATE_DISCARD_ENDINGS:
                if not Post.objects.filter(messageid=post[4]).exists():
                    try:
                        if self.add_post(post[0], post[4], logger=lambda x: logger('  %s'%x)):
                            last_added = post[0]
                    except socket.error as e:
                        if e.errno == errno.ECONNRESET:
                            # this happens, just reconnect and proceed
                            self.disconnect()
                            self.connect()
                            index -= 1
                        else:
                            raise
            #else:
            #    if self.add_post(post[0], post[4]):
            #        raise Exception("Discarded real post!")
            index += 1
        return last_added

    def get_post_header(self, header, post):
        index = 0
        h = '%s: ' % header
        while not post[3][index].startswith(h) and index < len(post[3]):
            index += 1
        assert post[3][index].startswith(h), \
            "Post %s does not have a '%s' header!" % (post[2], header)
        return post[3][index][len(h):]

    def add_post(self, postnumber, messageid, logger=noop):
        "Add a new post to the database (not post a new post)"
        try:
            post = self._nntp.article(messageid)
        except (nntplib.NNTPError, socket.error) as e:
            # TODO: don't give up so easily
            return False
        # check for dispose messages
        subject = self.get_post_header('Subject', post)
        if subject.startswith('DISPOSE '): # and '@' in subject:
            # it's a dispose message
            dispose_messageid = '<%s>'%subject[len('DISPOSE '):]
            try:
                PostMarker.objects.create(
                    messageid = dispose_messageid,
                    person_id = '$%s' % self.get_post_header('From', post),
                    is_good = False,
                )
            except IntegrityError:
                # this marker must already exist
                pass
            return False
        # if this isn't a dispose message, add it as a real post
        try:
            raw = RawPost(postnumber, post)
        except InvalidPost as e:
            return False
        snp = Post.from_raw(raw)
        try:
            snp.save()
        except IntegrityError:
            # this post must already exist
            return False
        else:
            logger("Added post: %s" % (raw.messageid))
            return True

    def get_raw_post(self, messageid):
        try:
            post = self._nntp.article(messageid)
        except (nntplib.NNTPError, socket.error) as e:
            raise ConnectionError(e)
        else:
            return RawPost(None, post) # TODO: maybe we do need the postnumber?...

    def verify_post(self, post):
        keys = settings.VERIFICATION_KEYS
        if keys is None or len(keys) == 0:
            return True
        else:
            raise NotImplementedError # TODO



    # public functionality methods

    def get_nzb(self, post):
        "Retrieves the nzb for a post, returned is the nzb content"
        assert self.is_connected()
        zipped = StringIO() # TODO: maybe replace this with os.tmpfile
        for messageid in post.nzb:
            self._nntp.body('<%s>'%messageid, zipped)
        content = zipped.getvalue()
        del zipped

        # decompression used is slightly different
        # from the python implementation
        # after a long night, this finally worked...
        content = content.replace(chr(10), '')
        content = content.replace('=C', '\n')
        content = content.replace('=B', '\r')
        content = content.replace('=A', '\0')
        content = content.replace('=D', '=')
        try:
            decompressed = zlib.decompress(content, -zlib.MAX_WBITS)
        except zlib.error as e:
            raise ConnectionError(e)
        else:
            return decompressed

    def get_comments(self, post):
        "Retrieves the comments for a post"
        assert self.is_connected()
        raise NotImplementedError # TODO



    # internal utility methods

    def get_last_messageid_in_db(self):
        try:
            snp = Post.objects.order_by('-posted').only('messageid')[0]
        except IndexError:
            return None
        else:
            return snp.messageid

    def get_last_postnumber_in_db(self):
        # to be server independend,
        # we get the last messageid
        # and then get the corresponding
        # postnumber
        messageid = self.get_last_messageid_in_db()
        if messageid is None:
            return None
        try:
            stat = self._nntp.stat(messageid)
        except (nntplib.NNTPError, socket.error) as e:
            return None
        else:
            return stat[1]

    def set_last_postnumber_in_db(self, last_added):
        if settings.UPDATE_LAST_STORAGE:
            raise NotImplementedError





