from django.urls import path

from . import views

app_name = "stations"
urlpatterns = [
    path("", views.list_stations, name="list"),
    path("<int:station_id>", views.station_details, name="details"),
    path("new/", views.edit_station, name="new"),
    path("edit/<int:station_id>", views.edit_station, name="edit"),
    path("delete/<int:station_id>", views.delete_station, name="delete"),
]
