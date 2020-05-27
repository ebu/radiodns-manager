from django.db import models


class Schedule(models.Model):
    start_date = models.DateTimeField()
    length = models.IntegerField()


class Show(models.Model):
    medium_name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=7)

    schedules = models.ManyToManyField(Schedule)
