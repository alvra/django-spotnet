import unittest


def suite():
    import os
    return unittest.defaultTestLoader.discover(os.path.dirname(__file__), '*.py')
