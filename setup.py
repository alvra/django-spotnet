from distutils.core import setup


setup(
    name='django-spotnet',
    version='0.1',
    description='An full-featured application for Django to handle spotnet posts.',
    author='Alexander van Ratingen',
    author_email='alexander@van-ratingen.nl',
    url='http://www.bitbucket.org/Blue/django-spotnet/',
    download_url='http://www.bitbucket.org/Blue/django-spotnet/',
    packages=[
        'spotnet',
        'spotnet.downloadserver',
        'spotnet.management',
        'spotnet.management.commands',
        'spotnet.tests',
    ],
    package_data={'spotnet': [
        'templates/spotnet/*.html',
        'static/*',
        'locale/*/LC_MESSAGES/*',
    ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
