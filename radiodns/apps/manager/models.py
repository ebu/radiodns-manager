from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    codops = models.CharField(max_length=255)

    short_name = models.CharField(max_length=8)
    medium_name = models.CharField(max_length=16)
    long_name = models.CharField(max_length=128)
    short_description = models.CharField(max_length=180)
    long_description = models.CharField(max_length=1200)
    url_default = models.CharField(max_length=255)

    postal_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=128)

    keywords = models.CharField(max_length=255)
    default_language = models.CharField(max_length=5)
    location_country = models.CharField(max_length=5)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{self.medium_name} {self.codops}"


class LogoImage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)

    url = models.URLField()


class User(AbstractUser):

    current_organization = models.ForeignKey(
        Organization, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}: {self.email}"

    @property
    def organizations_list(self):
        return list(self.organization_set.all())

    @property
    def active_organization(self):
        if not self.current_organization:
            self.current_organization = self.organization_set.first()
        return self.current_organization

    @active_organization.setter
    def active_organization(self, organization):
        self.current_organization = organization
