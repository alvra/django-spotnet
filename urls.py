from django.conf.urls.defaults import *


urlpatterns = patterns('django-spotnet.views',
    url(r'^$', 'index', name="index"),
    url(r'^(?P<page>[0-9]+)/$', 'index', name="index.page"),

    url(r'^post/(?P<id>[0-9]+)/$', 'viewpost', name="viewpost"),
)


