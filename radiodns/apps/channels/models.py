from django.db import models

from apps.manager.models import Organization
from apps.stations.models import Station


class Channel(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    TYPE_ID_CHOICES = [
        ("fm", "VHF/FM", ["ecc_id", "pi", "frequency"]),
        (
            "dab",
            "DAB",
            ["ecc_id", "eid", "sid", "scids", "appty_uatype", "pa", "mime_type"],
        ),
        ("drm", "DRM", ["sid"]),
        ("amss", "AMSS", ["sid"]),
        ("hd", "HD Radio", ["cc", "tx", "mid"]),
        (
            "id",
            "IP",
            ["fqdn", "serviceIdentifier", "stream_url", "mime_type", "bitrate"],
        ),
    ]
    TO_IGNORE_IN_DNS = ["stream_url", "mime_type", "bitrate"]

    type_id = models.CharField(max_length=5)

    # FM

    pi = models.CharField(max_length=4)
    frequency = models.CharField(max_length=5)

    # DAB/DAB+
    eid = models.CharField(max_length=4)
    sid = models.CharField(max_length=8)
    scids = models.CharField(max_length=3)
    appty_uatype = models.CharField(max_length=6)
    pa = models.IntegerField()

    # IP
    stream_url = models.CharField(max_length=255)
    bitrate = models.IntegerField()
    mime_type = models.CharField(max_length=64)

    # hd
    tx = models.CharField(max_length=5)
    cc = models.CharField(max_length=3)
    mid = models.IntegerField()

    # ID
    fqdn = models.CharField(max_length=255)
    serviceIdentifier = models.CharField(max_length=16)


class Ecc(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    iso = models.CharField(max_length=2)
    pi = models.CharField(max_length=2)
    ecc = models.CharField(max_length=3)


class Picture(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    filename = models.CharField(max_length=255)
    radiotext = models.CharField(max_length=255)
    radiolink = models.CharField(max_length=255)
    image_url_prefix = models.CharField(max_length=255)
