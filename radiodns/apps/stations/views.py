from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from apps.stations.forms import StationForm
from apps.stations.models import Station


@login_required
def list_stations(request):
    stations = Station.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(request, "stations/home.html", context={"stations": stations})


# STATION
@login_required
def station_details(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    return render(request, "stations/details.html", context={"station": station})


# EDIT ADD STATION
@login_required
def edit_station(request, station_id=None):
    station = None
    if station_id is not None:
        station = get_object_or_404(Station, id=station_id)
    form = StationForm(instance=station)
    if request.method == "POST":
        form = StationForm(request.POST, instance=station)
        if form.is_valid():
            form.save()
            return redirect("stations:list")
    return render(
        request,
        "stations/edit.html",
        context={"form": form, "organization": request.user.active_organization},
    )


# DELETE STATION
@login_required
def delete_station(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    station.delete()
    station.save()
    return redirect("stations:list")
