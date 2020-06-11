from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from apps.channels.models import Channel
from apps.manager.models import LogoImage
from apps.radioepg.forms import ShowForm, ServiceForm
from apps.radioepg.models import (
    Show,
    Event,
    GenericServiceFollowingEntry as Service,
    COLORS,
)
from apps.stations.models import Station


def ScheduleView(request, station_id=None):
    selected_station = None
    shows = None
    stations = Station.objects.filter(
        organization__id=request.user.active_organization.id
    )
    if station_id is None and len(stations) > 0:
        selected_station = list(stations)[0]
    else:
        selected_station = stations.filter(id=station_id).first()
    if selected_station is not None:
        shows = Show.objects.filter(
            station__id=selected_station.id,
            station__organization__id=request.user.active_organization.id,
        )
    return render(
        request,
        "radioepg/shows/home.html",
        context={
            "stations": stations,
            "selected_station": selected_station,
            "shows": shows,
        },
    )


def ShowsListView(request, station_id):
    stations = Station.objects.filter(
        organization__id=request.user.active_organization.id
    )
    selected_station = stations.filter(id=station_id).first()
    shows = Show.objects.filter(
        station__id=selected_station.id,
        station__organization__id=request.user.active_organization.id,
    )
    return render(
        request,
        "radioepg/shows/show_list.html",
        context={
            "stations": stations,
            "selected_station": selected_station,
            "shows": shows,
        },
    )


def EditShowView(request, station_id, show_id=None):
    selected_show = None
    if show_id is not None:
        selected_show = get_object_or_404(
            Show,
            id=show_id,
            station__organization__id=request.user.active_organization.id,
        )
    form = ShowForm(instance=selected_show)
    station = get_object_or_404(
        Station, id=station_id, organization__id=request.user.active_organization.id
    )
    if request.method == "POST":
        form = ShowForm(request.POST, instance=selected_show)
        if form.is_valid():
            show = form.save(commit=False)
            show.station = station
            show.save()
            return redirect("radioepg:list_shows", station_id=station_id)
    return render(
        request,
        "radioepg/shows/edit.html",
        context={"form": form, "selected_station": station, "colors": COLORS},
    )


def DeleteShowView(request, station_id, show_id):
    show = get_object_or_404(
        Show, id=show_id, station__organization__id=request.user.active_organization.id
    )
    show.delete()
    return redirect("radioepg:list_shows", station_id=station_id)


def ListServicesView(request, station_id=None):
    selected_station = None
    services = None
    stations = Station.objects.filter(
        organization__id=request.user.active_organization.id
    )
    if station_id is None and len(stations) > 0:
        selected_station = list(stations)[0]
    else:
        selected_station = stations.filter(id=station_id).first()
    if selected_station is not None:
        services = Service.objects.filter(
            station__id=selected_station.id,
            station__organization__id=request.user.active_organization.id,
        )
    return render(
        request,
        "radioepg/servicefollowing/home.html",
        context={
            "stations": stations,
            "selected_station": selected_station,
            "services": services,
        },
    )


def EditServiceView(request, station_id, service_id=None):
    selected_service = None
    if service_id is not None:
        selected_service = get_object_or_404(Service, id=service_id,)
    form = ServiceForm(instance=selected_service)
    station = get_object_or_404(Station, id=station_id)
    channels = Channel.objects.filter(station__id=station_id)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=selected_service)
        if form.is_valid():
            service = form.save(commit=False)
            service.active = True
            service.station = station
            service.save()
            return redirect("radioepg:station_services", station_id=station.id)
    return render(
        request,
        "radioepg/servicefollowing/edit.html",
        context={"form": form, "selected_station": station, "channels": channels},
    )


def TurnoffServiceView(request, station_id, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.active = False
    service.save()
    return redirect("radioepg:station_services", station_id=station_id)


def TurnonServiceView(request, station_id, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.active = True
    service.save()
    return redirect("radioepg:station_services", station_id=station_id)


def ListStationLogosView(request):
    stations = list(
        Station.objects.filter(organization__id=request.user.active_organization.id)
    )
    images = LogoImage.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(
        request,
        "radioepg/logos/logos.html",
        context={"stations": stations, "logos": images},
    )


def SetStationLogoView(request, station_id, logo_id):
    station = get_object_or_404(
        Station, id=station_id, organization__id=request.user.active_organization.id
    )
    logo = None
    if logo_id != 0:
        logo = get_object_or_404(
            LogoImage, id=logo_id, organization__id=request.user.active_organization.id
        )
    station.default_image = logo
    station.save()
    return JsonResponse({"station_id": station_id, "logo_id": logo_id})


def NewEventView(request, station_id):
    show_id = int(request.GET.get("show_id"))
    show = Show.objects.filter(id=show_id, station__id=station_id).first()
    event = Event()
    event.show = show
    event.day = int(request.GET.get("timeday"))
    event.start_hour = int(request.GET.get("hour"))
    event.start_minute = int(request.GET.get("minute"))
    event.length = 60
    event.save()
    return JsonResponse({})


def ResizeEventView(request, station_id):
    event_id = int(request.GET.get("event_id"))
    event = Event.objects.filter(id=event_id, show__station__id=station_id).first()
    event.length += int(request.GET.get("deltaMinutes"))
    event.save()
    return JsonResponse({})


def MoveEventView(request, station_id):
    event_id = int(request.GET.get("event_id"))
    event = Event.objects.filter(id=event_id, show__station__id=station_id).first()
    event.start_hour = int(request.GET.get("hour"))
    event.start_minute = int(request.GET.get("minute"))
    event.day += int(request.GET.get("deltaDay"))
    event.save()
    return JsonResponse({})


def DeleteEventView(request, station_id):
    event_id = int(request.GET.get("event_id"))
    event = Event.objects.filter(id=event_id, show__station__id=station_id)
    event.delete()
    return JsonResponse({})


def ListEventsView(request, station_id):
    events = list(Event.objects.filter(show__station__id=station_id))
    start = int(request.GET.get("start"))
    events_list = [
        {
            "id": event.id,
            "title": event.show.medium_name,
            "start": start + event.seconds_from_base,
            "end": start + event.seconds_from_base + event.length * 60,
            "allDay": False,
            "color": event.show.color,
            "textColor": "#000",
        }
        for event in events
    ]
    return JsonResponse({"list": events_list})
