from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class Organization(models.Model):
    """Model for organisations"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, blank=True)
    website = models.URLField(max_length=500, blank=True)
    codops = models.CharField(max_length=255, unique=True, null=True)
    logo = models.ImageField(upload_to='uploads/orgalogos', blank=True)

    def __str__(self):
        return """[{codops}] {name}""".format(codops=self.codops, name=self.name)


class LppUser(AbstractUser):
    organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username
