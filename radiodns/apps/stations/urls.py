from django.urls import path

from . import views

app_name = "stations"
urlpatterns = [
    path("", views.ListStationsView, name="list"),
    path("<int:station_id>", views.StationDetailsView, name="details"),
    path("new/", views.EditStationView, name="new"),
    path("edit/<int:station_id>", views.EditStationView, name="edit"),
    path("delete/<int:station_id>", views.DeleteStationView, name="delete"),
]
