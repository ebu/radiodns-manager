from django.urls import path

from . import views

app_name = "channels"
urlpatterns = [
    path("", views.ListChannelsView, name="list"),
    path("edit/<int:channel_id>", views.EditChannelView, name="edit"),
    path("new/", views.EditChannelView, name="new"),
    path("delete/<int:channel_id>", views.DeleteChannelView, name="delete"),
    path("export/", views.ExportChannelsView, name="export")
]
