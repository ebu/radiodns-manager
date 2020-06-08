from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

from apps.manager.models import LogoImage
from apps.stations.forms import StationForm
from apps.stations.models import Station


def ListStationsView(request):
    stations = Station.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(request, "stations/home.html", context={"stations": stations})


def StationDetailsView(request, station_id):
    station = get_object_or_404(
        Station, id=station_id, organization__id=request.user.active_organization.id
    )
    images = LogoImage.objects.filter(organization__id=request.user.active_organization.id)
    return render(request, "stations/details.html", context={"station": station, "images":images })


def EditStationView(request, station_id=None):
    station = None
    if station_id is not None:
        station = get_object_or_404(
            Station, id=station_id, organization__id=request.user.active_organization.id
        )
    form = StationForm(instance=station)
    if request.method == "POST":
        form = StationForm(request.POST, instance=station)
        print(form.errors)
        if form.is_valid():
            station = form.save(commit=False)
            station.organization = request.user.active_organization
            station.save()
            return redirect("stations:list")
    return render(
        request,
        "stations/edit.html",
        context={
            "form": form,
            "organization": request.user.active_organization,
            "languages": settings.LANGUAGES,
            "countries": settings.COUNTRIES_N_CODES
        },
    )


def DeleteStationView(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    station.delete()
    return redirect("stations:list")
