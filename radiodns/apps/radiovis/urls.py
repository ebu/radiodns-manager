from django.urls import path
from . import views

app_name = "radiovis"
urlpatterns = [
    path("gallery/", views.ImageListView, name="list_images"),
    path("edit/<int:image_id>", views.EditImageView, name="edit_image"),
    path("new/", views.EditImageView, name="new_image"),
    path("delete/<int:image_id>", views.DeleteImageView, name="delete_image"),
    path("channels/logs/<int:channel_id>", views.ChannelLogsView, name="channel_logs"),
    path("channels/", views.ListChannelsView, name="list_channels"),
    path(
        "channels/<int:channel_id>/set_image/<int:image_id>",
        views.SetChannelImageView,
        name="set_image",
    ),
]
