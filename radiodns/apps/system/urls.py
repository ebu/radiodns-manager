from django.urls import path

from . import views

app_name = "system"
urlpatterns = [path("", views.SystemStatusView, name="status"),
               path("check/", views.SystemCheckView, name="check")]
