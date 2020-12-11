import re

from django.http import Http404
from django.shortcuts import render

from apps.manager.models import Organization

# Create your views here.


def SiThreeView(request):
    hostname = request.META['HTTP_HOST']
    pattern = re.compile("([a-z0-9]{1,255})\.spi\.radio\.ebu\.io")

    matched = pattern.match(hostname)
    if matched is None:
        raise Http404("Invalid hostname please see https://www.etsi.org/deliver/etsi_ts/102800_102899/102818/03.01.01_60/ts_102818v030101p.pdf")
    else:
        service_provider = Organization.objects.select_related().get(codops=matched.group(1))

    def flatten(channel_set):
        res = []
        for channel in channel_set.all():
            for service_following in channel.genericservicefollowingentry_set.all():
                res.append([channel.epg_uri, service_following])
        return res

    stations = list(map(lambda x: [x.stationinstance_set.get(),
                                   x,
                                   flatten(x.channel_set)
                                   ], service_provider.station_set.select_related().all()))

    return render(
        request,
        "xml3.html",
        context={
            "service_provider": service_provider,
            "stations": stations,
            "service_provider_images": service_provider.logoimage_set.first(),
            "media_root": "/media/"
        },
    )
