from django.db import models

from apps.channels.models import Channel
from apps.stations.models import Station


class Show(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

    medium_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=7)


class Event(models.Model):
    day = models.IntegerField()
    start_hour = models.IntegerField()
    start_minute = models.IntegerField()
    length = models.IntegerField()

    show = models.ForeignKey(Show, on_delete=models.CASCADE)

    @property
    def seconds_from_base(self):
        """The number, in seconds of start, based on monday 00:00"""
        return self.day * 24 * 60 * 60 + self.start_hour * 60 * 60 + self.start_minute * 60


class GenericServiceFollowingEntry(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    active = models.BooleanField()
    cost = models.IntegerField()
    offset = models.IntegerField()
    mime_type = models.CharField(max_length=255, blank=True)
    bitrate = models.IntegerField(null=True, blank=True)
