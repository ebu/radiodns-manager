from django.db import models

from apps.manager.models import Organization


class Client(models.Model):
    name = models.CharField(max_length=500)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=128)
    email = models.CharField(max_length=255)
