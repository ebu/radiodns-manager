from django.urls import path

from . import views


app_name = "common"
urlpatterns = [
    path("terms/", views.TermsView, name="terms"),
    path("setup_error/", views.SetupErrorView, name="SetupErrorView"),
]
