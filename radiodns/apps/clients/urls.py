from django.urls import path

from . import views

app_name = "clients"
urlpatterns = [
    path("", views.ListClientsView, name="list"),
    path("edit/<int:client_id>", views.EditClientView, name="edit"),
    path("new/", views.EditClientView, name="new"),
    path("delete/<int:client_id>", views.DeleteClientView, name="delete"),
]
