from django.urls import path

from . import views

app_name = "radiodns_auth"
urlpatterns = [
    path("login/", views.LoginView, name="login"),
    path("logout/", views.LogoutView, name="logout"),
    path("xml-metadata/", views.SamlMetadataView, name="xml"),
]
