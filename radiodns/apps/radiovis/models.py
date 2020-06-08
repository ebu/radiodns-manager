import datetime

from django.db import models

from apps.channels.models import Channel
from apps.manager.models import Organization



class LogEntry(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    body = models.TextField()
    headers = models.TextField()
    reception_timestamp = models.FloatField()

    @property
    def reception_date(self):
        return datetime.datetime.fromtimestamp(self.reception_timestamp)
