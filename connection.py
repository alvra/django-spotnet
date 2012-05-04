import nntplib, socket, errno
import settings
import zlib
from cStringIO import StringIO
from django.db import IntegrityError
from models import SpotnetPost, PostMarker
from post import SpotnetRawPost, InvalidPost

import os, logging
logging.basicConfig(
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)) ,'..', 'spotweb.log'), 
    #level = logging.WARNING,
    #level = logging.INFO,
    level = logging.DEBUG,
)

try:
    import colors
    print_log_colors = dict(
        debug =    colors.green,
        info =     colors.blue,
        warning =  colors.purple,
        error =    colors.red,
        critical = colors.light_red, # isn't this more noticable than red...
    )
except ImportError:
    print_log_colors = {}

# TODO:
# maybe decode headers using a function (new in python 3?)
# http://docs.python.org/py3k/library/nntplib.html?highlight=nntp#nntplib.decode_header





NEWSSERVER_UNAUTH_USERNAME = None
NEWSSERVER_UNAUTH_PASSWORD = None





class SpotnetComment(object):
    def __init__(self, post, author, message):
        self.post = post
        self.author = author
        self.message = message





#
# We are working with two types of id's here
#
# - messageid : universally unique id, eg: '<3ae6b2dcccdf42988a85dc314370ba0123@free.pt>'
# - postnumber : server dependend id, eg: '65903' (always use strings in nntplib!)
#

class SpotnetConnection(object):
    ""

    def __init__(self, connect=True, log_print=False, log_logging=True):
        self.log_print = log_print
        self.log_logging = log_logging
        self._nntp = None
        if connect:
            self.connect()

    def is_connected(self):
        return self._nntp is not None

    def connect(self):
        # connect to server
        try:
            nntp = nntplib.NNTP(
                host = settings.SERVER_HOST,
                port = settings.SERVER_PORT,
                readermode = settings.SERVER_READERMODE,
                usenetrc = False,
            )
        except nntplib.NNTPError as e:
            self.log('error', "Error at connecting: %s" % e)
            return
        else:
            self.log('info', 'Connected to newsserver')
        # try to encrypt connection using ssl
        if hasattr(nntp, 'starttls'):
            nntp.starttls(ssl_context=None)
            self.log('info', 'Encrypted connection to newsserver')
        else:
            self.log('info', 'Unable to encrypt connection to newsserver')
        # login, now that we might be encrypted
        try:
            nntp.login(
                user = settings.SERVER_USERNAME if settings.SERVER_USERNAME is not None else NEWSSERVER_UNAUTH_USERNAME,
                password = settings.SERVER_PASSWORD if settings.SERVER_PASSWORD is not None else NEWSSERVER_UNAUTH_PASSWORD,
            )
        except nntplib.NNTPError as e:
            self.log('error', "Error at logging in: %s" % e)
            return
        else:
            self.log('info', 'Logged into newsserver')
        self._nntp = nntp

    def disconnect(self):
        if self.is_connected():
            try:
                msg = self._nntp.quit()
            except EOFError:
                # seems to happen for me, but we're still disconnected
                # TODO: find a way to check if we're really disconnected
                # and rethrow the exception if not
                self.log('warning', 'Ignored an EOFError while disconnecting to newsserver %s' % repr(settings.SERVER_HOST))
            else:
                self.log('info', 'Disconnected from newsserver with message %s' % repr(msg))
            self._nntp = None

    def log(self, logtype, message):
        if self.log_print:
            color = print_log_colors.get(logtype, lambda x: x)
            print '%s: %s' % (color(logtype.capitalize()), message)
        if self.log_logging:
            getattr(logging, logtype)(message)

    def update(self):
        "Retrieves all new posts."
        self.log('info', 'Started updating')
        for group in settings.UPDATE_GROUPS:
            self.update_group(group)

    def update_group(self, groupname):
        self.log('info', 'Started updating group %s' % repr(groupname))
        try:
            gresp = self._nntp.group(groupname)
        except nntplib.NNTPError as e:
            self.log('error', "Error at command 'GROUP': %s" % e)
            return
        else:
            self.log('debug', "Set group to '%s', response was '%s'" % (groupname,gresp))
        first_on_server,last = gresp[2],gresp[3] # first < last
        last_in_db = self.get_last_postnumber_in_db()

        first_options = [int(first_on_server)]
        if last_in_db is not None:
            first_options.append(int(last_in_db))
        if settings.UPDATE_MINPOST is not None:
            first_options.append(settings.UPDATE_MINPOST)
        first = max(first_options)

        self.log('info', 'Iterating postnumbers %s to %s' % (first, last))

        last = int(last)
        curstart = first
        last_added = None
        while curstart < last + 15000:
            x = self.update_group_postnumbers(groupname, curstart, curstart+settings.UPDATE_BULK_COUNT)
            if x:
                last_added = x
            curstart += settings.UPDATE_BULK_COUNT
        # store last added post's postnumber
        # since there's not always a way to obtain it
        # from the last messageid alone
        if settings.UPDATE_LAST_STORAGE:
            # TODO
            pass

    def update_group_postnumbers(self, groupname, start, end):
        self.log('info', 'Checking postnumbers block %s to %s' % (start, end))
        try:
            xover = self._nntp.xover(str(start), str(end))
        except nntplib.NNTPError as e:
            self.log('error', "Error at command 'XOVER': %s" % e)
            return
        last_added = None
        index = 0
        while index < len(xover[1]):
            spot = xover[1][index]
            # we limit ourselves only to posts that are
            # actually from the right group
            # apparently, that's not always guarantied
            if spot[4][:-1].split('@',1)[-1] not in ('news.hitnews.eu'):
            #if spot[4][:-1].endswith('@'+groupname):
                if not SpotnetPost.objects.filter(messageid=spot[4]).exists():
                    try:
                        if self.add_post(spot[0], spot[4]):
                            last_added = spot[0]
                    except socket.error as e:
                        if e.errno == errno.ECONNRESET:
                            self.log('warning', "Connection was reset by peer")
                            # this happens, just reconnect and retry
                            self.disconnect()
                            self.connect()
                            index -= 1
                        else:
                            self.log('warning', "Unknown error with the underlying socket: '%s'" % repr(e))
                            raise
                else:
                    self.log('debug', 'Skipping existing post %s, number %s' % (spot[4], spot[0]))
            #else:
            #    #if not SpotnetPost.objects.filter(messageid=spot[4]).exists():
            #    if self.add_post(spot[0], spot[4]):
            #        raise Exception("Found spot in other group!")
            index += 1
        return last_added

    def get_nzb(self, spot):
        "Retrieves the nzb for a spot, returned is the nzb content"
        assert self.is_connected()
        zipped = StringIO()
        for messageid in spot.nzb:
            self._nntp.body('<%s>'%messageid, zipped)
        content = zipped.getvalue()
        del zipped

        content = content.replace(chr(10), '')

        # set content to right stuff
        if not True:
            with open('/tmp/spotweb_nzb_1.nzb', 'r') as f:
                content = f.read()

        #with open('/tmp/omesium_nzb_1.nzb', 'w') as f:
        #    f.write(content)
        content = content.replace('=C', '\n')
        content = content.replace('=B', '\r')
        content = content.replace('=A', '\0')
        content = content.replace('=D', '=')

        #print; print content; print
        #with open('/tmp/omesium_nzb_2.nzb', 'w') as f:
        #    f.write(content)
        try:
            #decompressed = zlib.decompress(content) # Error -3 while decompressing data: unknown compression method
            #decompressed = zlib.decompress('x\x9c' + content) # Error -5 while decompressing data: incomplete or truncated stream
            #decompressed = zlib.decompressobj().decompress(content) # Error -3 while decompressing: unknown compression method
            #decompressed = zlib.decompressobj().decompress('x\x9c' + content) # WORKS!
            decompressed = zlib.decompress(content, -zlib.MAX_WBITS) # WORKS!

            #with open('/tmp/omesium_nzb_3.nzb', 'w') as f:
            #    f.write(decompressed)
        except zlib.error as e:
            self.log('error', "Error at decompressing nzb: %s" % e)
            return None
        else:
            return decompressed

    def get_comments(self, spot):
        "Retrieves the comments for a spot"
        assert self.is_connected()
        pass # TODO

    def get_post_header(self, header, post):
        index = 0
        h = '%s: ' % header
        while not post[3][index].startswith(h) and index < len(post[3]):
            index += 1
        assert post[3][index].startswith(h), "Post %s does not have a '%s' header!" % (post[2],header)
        return post[3][index][len(h):]

    def add_post(self, postnumber, messageid):
        "Add a new spot to the database (not post a new spot)"
        try:
            post = self._nntp.article(messageid)
        except nntplib.NNTPError as e:
            self.log('error', "Error at command 'ARTICLE': %s" % e)
            return False
        # check for dispose messages
        subject = self.get_post_header('Subject', post)
        if subject.startswith('DISPOSE ') and '@' in subject:
            # it's a dispose message
            dispose_messageid = '<%s>'%subject[len('DISPOSE '):]
            self.log('info', 'Found dispose message for post %s, number %s' % (messageid, postnumber))
            try:
                PostMarker.objects.create(
                    messageid = dispose_messageid,
                    person_id = '$%s' % self.get_post_header('From', post),
                    is_good = False,
                )
            except IntegrityError:
                self.log('debug', 'Trying to add an existing dispose message %s, number %s' % (messageid, postnumber))
                pass
            return False
        # if this isn't a dispose message, add it as a real post
        try:
            raw = SpotnetRawPost(postnumber, post)
        except InvalidPost as e:
            self.log('debug', "Found invalid post %s, number %s. Exception was '%s'" % (messageid, postnumber, repr(e)))
            return False
        snp = SpotnetPost.from_spot(raw)
        try:
            snp.save()
        except IntegrityError:
            self.log('debug', 'Trying to add an existing post %s, number %s' % (messageid, postnumber))
            return False
        else:
            self.log('info', 'Adding raw post %s, number %s' % (messageid, postnumber))
            return True

    def verify_spot(self, spot):
        keys = settings.VERIFICATION_KEYS
        if keys is None or len(keys) == 0:
            return True
        else:
            pass # TODO

    def get_raw_post(self, messageid):
        try:
            post = self._nntp.article(messageid)
        except nntplib.NNTPError as e:
            self.log('error', "Error at command 'ARTICLE': %s" % e)
            return
        return SpotnetRawPost(None, post) # TODO: maybe we do need the postnumber?...

    # internal methods

    def get_last_messageid_in_db(self):
        try:
            snp = SpotnetPost.objects.order_by('-posted').only('messageid')[0]
        except KeyError:
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
        except nntplib.NNTPError:
            return None
        else:
            return stat[1]
        




