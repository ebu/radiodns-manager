from django.db import models


class Ecc(models.Model):
    name = models.CharField(max_length=255)
    iso = models.CharField(max_length=2)
    pi = models.CharField(max_length=2)
    ecc = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.iso.upper()} {self.name} [{self.ecc}]"


class Language(models.Model):
    name = models.CharField(max_length=255)
    iso = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.iso.upper()} - {self.name}"
