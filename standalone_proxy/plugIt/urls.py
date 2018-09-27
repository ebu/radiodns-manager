# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'', include('plugit_proxy.urls')),
)
