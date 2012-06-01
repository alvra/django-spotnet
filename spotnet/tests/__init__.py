import unittest


def suite():
    import os
    loader = unittest.defaultTestLoader
    if hasattr(loader, 'discover'):
        return loader.discover(os.path.dirname(__file__), '*.py')
    else:
        # for compatibility with python 2.6
        s = loader.loadTestsFromName('spotnet.tests')
        for name in os.listdir(os.path.dirname(__file__)):
            if name.endswith('.py'):
                s.addTest(loader.loadTestsFromName('spotnet.tests.%s' % name[:-3]))
        return s


if __name__ == '__main__':
    # this would never work unless DJANGO_SETTINGS_MODULE is defined
    unittest.TextTestRunner(verbosity=2).run(suite())
