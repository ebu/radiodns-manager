from django.shortcuts import render, get_object_or_404, redirect

from apps.clients.models import Client
from apps.localization.models import Language, Ecc
from apps.manager.models import LogoImage
from apps.stations.forms import StationInstanceForm, StationForm
from apps.stations.models import Station, StationInstance


def ListStationsView(request):
    stations = Station.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(request, "stations/home.html", context={"stations": stations})


def StationDetailsView(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    instances = StationInstance.objects.filter(station__id=station_id)
    images = LogoImage.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(
        request,
        "stations/details.html",
        context={"station": station, "instances": instances, "images": images},
    )


def EditStationView(request, station_id=None):
    client_instance_forms = []
    station_form = StationForm(instance=None, prefix="station")
    clients = Client.objects.filter(
        organization__id=request.user.active_organization.id
    )
    languages = Language.objects.all()
    countries = Ecc.objects.all()
    if station_id is not None:
        instances = StationInstance.objects.filter(
            station__id=station_id,
            station__organization__id=request.user.active_organization.id,
        )
        default_instance = instances.filter(client_id=None).first()
        client_instance_forms.append(
            (
                Client.generate_default(request.user.active_organization),
                default_instance,
                StationInstanceForm(instance=default_instance, prefix="0"),
            )
        )

        for client in clients:
            client_instance = instances.filter(client__id=client.id).first()
            client_instance_forms.append(
                (
                    client,
                    client_instance,
                    StationInstanceForm(instance=client_instance, prefix=client.id),
                )
            )
        station = get_object_or_404(Station, id=station_id)
        station_form = StationForm(instance=station, prefix="station")
    else:
        client_instance_forms = [
            (
                Client.generate_default(request.user.active_organization),
                None,
                StationInstanceForm(prefix="0"),
            )
        ]
        for client in clients:
            client_instance_forms.append(
                (client, None, StationInstanceForm(prefix=client.id))
            )
    if request.method == "POST":
        client_forms = []
        for instance in client_instance_forms:
            if request.POST.get(f"{instance[0].id}-short_name") != "":
                client_forms.append(
                    (
                        instance[0],
                        StationInstanceForm(
                            request.POST,
                            instance=instance[1],
                            prefix=str(instance[0].id),
                        ),
                    )
                )
        station = None
        if station_id is None:
            station = Station(organization=request.user.active_organization)
        else:
            station = get_object_or_404(Station, id=station_id)
        sform = StationForm(request.POST, instance=station, prefix="station")
        if all([client[1].is_valid() for client in client_forms]) and sform.is_valid():
            station = sform.save()
            for client in client_forms:
                station_instance = client[1].save(commit=False)
                station_instance.station = station
                if client[0].id != 0:
                    station_instance.client = client[0]
                station_instance.save()
            return redirect("stations:details", station_id=station_id)
    return render(
        request,
        "stations/edit.html",
        context={
            "client_instance_forms": client_instance_forms,
            "station_form": station_form,
            "organization": request.user.active_organization,
            "languages": languages,
            "countries": countries,
            "station_id": station_id
        },
    )


def DeleteStationView(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    station.delete()
    return redirect("stations:list")


def DeleteStationInstanceView(request, instance_id):
    instance = get_object_or_404(StationInstance, id=instance_id)
    instance.delete()
    return redirect("stations:list")
