from django.db import models

from apps.manager.models import Organization
from apps.stations.models import Station


class Image(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    file = models.ImageField(blank=True, null=True)
    radiotext = models.CharField(max_length=255)
    radiolink = models.URLField()


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
    pi = models.CharField(max_length=4, blank=True, null=True)
    frequency = models.CharField(max_length=5, blank=True, null=True)

    # DAB/DAB+
    eid = models.CharField(max_length=4, blank=True, null=True)
    sid = models.CharField(max_length=8, blank=True, null=True)
    scids = models.CharField(max_length=3, blank=True, null=True)
    appty_uatype = models.CharField(max_length=6, blank=True, null=True)
    pa = models.IntegerField(blank=True, null=True)

    # IP
    stream_url = models.CharField(max_length=255, blank=True, null=True)
    bitrate = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=64, blank=True, null=True)

    # hd
    tx = models.CharField(max_length=5, blank=True, null=True)
    cc = models.CharField(max_length=3, blank=True, null=True)
    mid = models.IntegerField(blank=True, null=True)

    # ID
    fqdn = models.CharField(max_length=255, blank=True, null=True)
    serviceIdentifier = models.CharField(max_length=16, blank=True, null=True)

    default_image = models.ForeignKey(Image, on_delete=models.CASCADE, blank=True, null=True)


class Ecc(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    iso = models.CharField(max_length=2)
    pi = models.CharField(max_length=2)
    ecc = models.CharField(max_length=3)


