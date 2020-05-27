from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from apps.channels.forms import ChannelForm
from apps.channels.models import Channel


def list_channels(request):
    channels = Channel.objects.filter(
        station__organization__id=request.user.active_organization.id
    )
    return render(request, "channels/home.html", context={"channels": channels})


@login_required
def edit_channel(request, channel_id=None):
    channel = None
    if channel_id is not None:
        channel = get_object_or_404(Channel, id=channel_id)
    form = ChannelForm(instance=channel)
    if request.method == "POST":
        form = ChannelForm(request.POST, instance=channel)
        if form.is_valid():
            form.save()
            return redirect("channels:list")
    return render(request, "channels/edit.html", context={"form": form})


@login_required
def delete_channel(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    channel.delete()
    channel.save()
    return redirect("channels:list")


# TODO Add import export methods
