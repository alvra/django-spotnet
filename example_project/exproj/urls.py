try:
    from django.conf.urls import patterns, include, url
except ImportError as e:
    # django 1.3 compatibility
    try:
        from django.conf.urls.defaults import patterns, include, url
    except ImportError:
        raise e

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'exproj.index.views.index'),
    url(r'^spotnet/', include('spotnet.urls', namespace='spotnet')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

try:
    import rosetta
except ImportError:
    pass
else:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
