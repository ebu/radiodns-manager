from django.urls import path

from . import views

app_name = "manager"
urlpatterns = [
    path(
        "set-org/?<int:organization_id>",
        views.SetOrganizationView,
        name="SetOrganizationView",
    ),
    path("", views.OrganizationDetailsView, name="details"),
    path("edit/", views.EditOrganizationView, name="edit"),
    path("images/", views.ListImagesView, name="list_images"),
    path("images/new/", views.EditImageView, name="new_image"),
    path("images/edit/<int:image_id>", views.EditImageView, name="edit_image"),
    path("images/delete/<int:image_id>", views.DeleteImageView, name="delete_image"),
    path(
        "images/default/<int:image_id>",
        views.SetDefaultImageView,
        name="set_default_image",
    ),
]
