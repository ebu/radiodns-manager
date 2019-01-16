from django.urls import re_path

from plugIt import views

urlpatterns = [
    re_path(r'^ebuio_api/$', views.api_home, name="api_home"),

    re_path(r'^orga/(?P<orga_pk>-?[0-9]+)$', views.api_orga, name='api_orga'),
    re_path(r'^ebuio_api/orga/(?P<orga_pk>-?[0-9]+)$', views.api_orga, name='api_orga'),
    re_path(r'^media/(?P<path>.*)$', views.media, name="media"),
    re_path(r'^(?P<query>.*)$', views.main, name="main"),
]
