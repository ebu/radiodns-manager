from django.urls import path

from . import views

app_name = "manager"
urlpatterns = [
    path(
        "set-org/?<int:organization_id>",
        views.set_organization,
        name="set_organization",
    ),
    path("", views.organization_details, name="details"),
    path("edit/", views.edit_organization, name="edit"),
]
