from django.urls import path

from . import views

app_name = "si_pi"
urlpatterns = [
    path("spi/3.1/SI.xml", views.SiThreeView, name="si_version_three"),
    path("epg/XSI.xml", views.SiOneView, name="si_version_one"),
    path("spi/3.1/<path:path>/<int:date>_PI.xml", views.PiThreeView, name="pi_version_three"),
    path("epg/<path:path>/<int:date>_PI.xml", views.PiOneView, name="pi_version_one"),
]
