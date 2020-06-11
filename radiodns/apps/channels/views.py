from django.shortcuts import render, redirect, get_object_or_404

from apps.channels.forms import ChannelForm
from apps.channels.models import Channel
from apps.clients.models import Client
from apps.localization.models import Ecc
from apps.stations.models import Station


def ListChannelsView(request):
    channels = Channel.objects.filter(
        station__organization__id=request.user.active_organization.id
    )
    return render(request, "channels/home.html", context={"channels": channels})


def EditChannelView(request, channel_id=None):
    channel = None
    if channel_id is not None:
        channel = get_object_or_404(
            Channel,
            id=channel_id,
            station__organization__id=request.user.active_organization.id,
        )
    countries = Ecc.objects.all()
    form = ChannelForm(instance=channel)
    if request.method == "POST":
        form = ChannelForm(request.POST, instance=channel)
        if form.is_valid():
            selected_country = countries.filter(iso=form.cleaned_data["ecc"])
            selected_station = Station.objects.filter(id=form.cleaned_data["station"])
            channel = form.save(commit=False)
            channel.ecc = selected_country
            channel.station = selected_station
            channel.save()
            return redirect("channels:list")
    return render(
        request,
        "channels/edit.html",
        context={
            "form": form,
            "types_id": Channel.TYPE_ID_CHOICES,
            "stations": Station.all_stations_in_organization(
                request.user.active_organization.id
            ),
            "clients": Client.all_clients_in_organization(
                request.user.active_organization.id
            ),
            "countries": countries,
        },
    )


def DeleteChannelView(request, channel_id):
    channel = get_object_or_404(
        Channel,
        id=channel_id,
        station__organization__id=request.user.active_organization.id,
    )
    channel.delete()
    return redirect("channels:list")


# TODO Add import export methods
