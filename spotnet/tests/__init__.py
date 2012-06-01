import unittest


def suite():
    import os
    return unittest.defaultTestLoader.discover( \
        os.path.dirname(__file__), '*.py')


if __name__ == '__main__':
    # this would never work unless DJANGO_SETTINGS_MODULE is defined
    unittest.TextTestRunner(verbosity=2).run(suite())
