from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from apps.channels.models import Channel, Image
from apps.radiovis.forms import ImageForm
from apps.radiovis.models import LogEntry
from common.utils import scale_image


def ImageListView(request):
    images = Image.objects.filter(organization__id=request.user.active_organization.id)
    return render(request, "radiovis/gallery/home.html", context={"images": images})


def EditImageView(request, image_id=None):
    selected_image = None
    if image_id is not None:
        selected_image = get_object_or_404(
            Image, id=image_id, organization__id=request.user.active_organization.id
        )
    form = ImageForm(instance=selected_image)
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES, instance=selected_image)
        if form.is_valid():
            image = form.save(commit=False)
            image.organization = request.user.active_organization
            image.file = scale_image(image.file, 320, 240)
            image.save()
            return redirect("radiovis:list_images")
    return render(request, "radiovis/gallery/edit.html", context={"form": form})


def DeleteImageView(request, image_id):
    image = get_object_or_404(
        Image, id=image_id, organization__id=request.user.active_organization.id
    )
    image.delete()
    return redirect("radiovis:list_images")


def ChannelLogsView(request, channel_id):
    logs = LogEntry.objects.filter(
        channel__id=channel_id,
        channel__station__organization__id=request.user.active_organization.id,
    )
    channel = get_object_or_404(
        Channel,
        id=channel_id,
        station__organization__id=request.user.active_organization.id,
    )
    return render(
        request,
        "radiovis/channels/logs.html",
        context={"logs": logs, "channel": channel},
    )


def ListChannelsView(request):
    channels = Channel.objects.filter(
        station__organization__id=request.user.active_organization.id
    )
    images = Image.objects.filter(organization__id=request.user.active_organization.id)
    return render(
        request, "radiovis/channels/home.html", context={"channels": channels, "images":images}
    )


def SetChannelImageView(request, channel_id, image_id):
    channel = get_object_or_404(Channel, id=channel_id, station__organization__id=request.user.active_organization.id)
    image = None
    if image_id != 0:
        image = get_object_or_404(Image, id=image_id, organization__id=request.user.active_organization.id)
    channel.default_image = image
    channel.save()
    return JsonResponse({"channel_id": channel_id, "image_id": image_id})
