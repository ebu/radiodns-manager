from django.urls import path

from . import views

app_name = "radioepg"
urlpatterns = [
    path("schedule/", views.ScheduleView, name="default_schedule"),
    path("schedule/<int:station_id>/", views.ScheduleView, name="station_schedule"),
    path("schedule/<int:station_id>/new/", views.NewEventView, name="create_event"),
    path(
        "schedule/<int:station_id>/resize/", views.ResizeEventView, name="resize_event"
    ),
    path("schedule/<int:station_id>/move/", views.MoveEventView, name="move_event"),
    path(
        "schedule/<int:station_id>/delete/", views.DeleteEventView, name="delete_event"
    ),
    path("schedule/<int:station_id>/events/", views.ListEventsView, name="list_events"),
    path("shows/<int:station_id>/", views.ShowsListView, name="list_shows"),
    path("shows/<int:station_id>/new/", views.EditShowView, name="new_show"),
    path(
        "shows/<int:station_id>/edit/<show_id>/", views.EditShowView, name="edit_show"
    ),
    path(
        "shows/<int:station_id>/delete/<show_id>/",
        views.DeleteShowView,
        name="delete_show",
    ),
    path("logos/", views.ListStationLogosView, name="station_logos"),
    path("logos/set/", views.SetStationLogoView, name="set_logo"),
    path("servicefollowing/", views.ListServicesView, name="default_services"),
    path(
        "servicefollowing/<int:station_id>/",
        views.ListServicesView,
        name="station_services",
    ),
    path(
        "servicefollowing/<int:station_id>/new/",
        views.EditServiceView,
        name="new_service",
    ),
    path(
        "servicefollowing/<int:station_id>/edit/<int:service_id>",
        views.EditServiceView,
        name="edit_service",
    ),
    path(
        "servicefollowing/<int:station_id>/turn_off/<int:service_id>",
        views.TurnoffServiceView,
        name="turnoff_service",
    ),
    path(
        "servicefollowing/<int:station_id>/turn_on/<int:service_id>",
        views.TurnonServiceView,
        name="turnon_service",
    ),
]
