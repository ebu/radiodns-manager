from django.urls import path

from . import views

app_name = "channels"
urlpatterns = [
    path("", views.list_channels, name="list"),
    path("edit/<int:channel_id>", views.edit_channel, name="edit"),
    path("new/", views.edit_channel, name="new"),
    path("delete/<int:channel_id>", views.delete_channel, name="delete"),
]
