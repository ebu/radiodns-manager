from django.urls import path

from . import views

app_name = "clients"
urlpatterns = [
    path("", views.list_clients, name="list"),
    path("edit/<int:client_id>", views.edit_client, name="edit"),
    path("new/", views.edit_client, name="new"),
    path("delete/<int:station_id>", views.delete_client, name="delete"),
]
