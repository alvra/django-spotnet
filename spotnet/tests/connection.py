try:
    from django.utils import unittest
except ImportError:
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
if not hasattr(unittest, 'expectedFailure'):
    unittest.expectedFailure = lambda f: f

from django.test import TestCase as DjangoTestCase
from mock import Mock
from spotnet import settings
from spotnet.connection import Connection, ConnectError


class ConnectionTestMixin(object):
    def get_conn(self):
        conn = Connection(connect=False)
        conn._nntp = Mock()
        return conn


class BasicConnectionTest(ConnectionTestMixin, unittest.TestCase):
    "Test some basic method of the Connection class."

    def test_get_post_header(self):
        conn = self.get_conn()
        # TODO

    def test_get_raw_post(self):
        conn = self.get_conn()
        conn._nntp.article.return_value = None
        # TODO

    def test_verify_post(self):
        conn = self.get_conn()
        # TODO

    def test_get_nzb(self):
        conn = self.get_conn()
        conn._nntp.body.return_value = None
        # TODO

    def test_get_comments(self):
        conn = self.get_conn()
        # TODO


class DbConnectionTest(ConnectionTestMixin, DjangoTestCase):
    "Test methods of the Connection class that use the db."

    def test_add_post(self):
        conn = self.get_conn()
        conn._nntp.article.return_value = None
        # TODO

    def test_get_last_messageid_in_db(self):
        conn = self.get_conn()
        # TODO

    def test_get_last_postnumber_in_db(self):
        conn = self.get_conn()
        conn._nntp.stat.return_value = None
        # TODO

    def test_set_last_messageid_in_db(self):
        conn = self.get_conn()
        # TODO


class ConnectionTest(ConnectionTestMixin, unittest.TestCase):
    """Test methods of the Connection class
    that must connect to a real nntp server.
    """

    @unittest.expectedFailure
    def test_connect_default(self):
        conn = self.get_conn()
        # backup previous settings
        prev_host = settings.SERVER_HOST
        prev_port = settings.SERVER_PORT
        prev_user = settings.SERVER_USERNAME
        prev_pasw = settings.SERVER_PASSWORD
        prev_rdrm = settings.SERVER_READERMODE

        # a free usenet server
        settings.SERVER_HOST = 'news.windstream.net'
        settings.SERVER_PORT = 119
        settings.SERVER_USERNAME = None
        settings.SERVER_PASSWORD = None
        settings.SERVER_READERMODE = False
        try:
            conn.connect()
        except ConnectError:
            self.fail("Could not connect to a free usenet server.")
        else:
            conn.disconnect()
        finally:
            # return to original settings
            settings.SERVER_HOST = prev_host
            settings.SERVER_PORT = prev_port
            settings.SERVER_USERNAME = prev_user
            settings.SERVER_PASSWORD = prev_pasw
            settings.SERVER_READERMODE = prev_rdrm

    @unittest.skipIf(
        settings.SERVER_HOST is None,
        "No usenet server defined in your settings file.",
    )
    def test_connect_current_settings(self):
        pass
