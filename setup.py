from distutils.core import setup
import os


packages, data_files = [], []
for dirpath, dirnames, filenames in os.walk(os.path.join(
    os.path.dirname(__file__),
    'spotnet',
)):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[len('spotnet/'):] # Strip "spotnet/" or "spotnet\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-spotnet',
      version='0.1',
      description='An full-featured application for Django to handle spotnet posts.',
      author='Alexander van Ratingen',
      author_email='alexander@van-ratingen.nl',
      url='http://www.bitbucket.org/Blue/django-spotnet/',
      download_url='http://www.bitbucket.org/Blue/django-spotnet/',
      package_dir={'spotnet': 'spotnet'},
      packages=packages,
      package_data={'spotnet': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License', # TODO
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )

