from django.urls import path

from . import views

app_name = "si_pi"
urlpatterns = [
    path("spi/3.1/SI.xml", views.SiThreeView, name="si_version_three"),
]
