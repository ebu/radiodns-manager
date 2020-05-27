from django.urls import path

from . import views


app_name = "common"
urlpatterns = [path("terms/", views.terms, name="terms")]
