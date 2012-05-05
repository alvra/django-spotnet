from django.conf.urls.defaults import *


urlpatterns = patterns('spotnet.views',
    url(r'^$', 'search', name="index"),
    url(r'^(?P<page>[0-9]+)/$', 'search', name="index"),

    url(r'^search/$', 'search', name="search"),
    url(r'^search/(?P<cats>[a-zA-Z,]+)/$', 'search', name="search"),
    url(r'^search/(?P<cats>[a-zA-Z,]+)/(?P<page>[0-9]+)/$', 'search', name="search"),
    url(r'^search/(?P<scats>[a-zA-Z,]+)/$', 'search', name="search"),
    url(r'^search/(?P<scats>[a-zA-Z,]+)/(?P<page>[0-9]+)/$', 'search', name="search"),
    url(r'^search/(?P<cats>[a-zA-Z,]+)/(?P<scats>[a-zA-Z,]+)/(?P<search>.+)/$', 'search', name="search"),
    url(r'^search/(?P<cats>[a-zA-Z,]+)/(?P<scats>[a-zA-Z,]+)/(?P<search>.+)/(?P<page>[0-9]+)/$', 'search', name="search"),

    url(r'^update/$', 'update', name="update"),

    url(r'^post/(?P<id>[0-9]+)/$', 'viewpost', name="viewpost"),
    url(r'^post/(?P<id>[0-9]+)/nzb/$', 'download_nzb', name="download_nzb"),
    url(r'^post/(?P<id>[0-9]+)/download/$', 'download', name="download"),
    url(r'^post/(?P<id>[0-9]+)/download/(?P<dls>[a-zA-Z0-9]+)/$', 'download', name="download_using"),

    url(r'^downloaded/$', 'downloaded', name='downloaded'),
)

