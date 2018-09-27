# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import RedirectView


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    (r'^$', RedirectView.as_view(url='/plugIt/')),
    url(r'^plugIt/', include('plugIt.urls')),

    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  # Never use this in prod !

    # Login - logout
    url(r'^ebuio_logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^ebuio_login$', 'django.contrib.auth.views.login'),

    # Default to PlugIt
    url(r'', include('plugIt.urls')),  # plugit
)
