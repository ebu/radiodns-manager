from django.conf import settings
from django.db import models

from apps.manager.models import Organization, LogoImage


class Station(models.Model):
    name = models.CharField(max_length=80)
    short_name = models.CharField(max_length=8)
    medium_name = models.CharField(max_length=16)
    long_name = models.CharField(max_length=128)
    short_description = models.CharField(max_length=180)
    url_default = models.URLField(blank=True, null=True)

    postal_name = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=25, blank=True, null=True)
    phone_number = models.CharField(max_length=128, blank=True, null=True)
    sms_number = models.CharField(max_length=128, blank=True, null=True)
    sms_body = models.CharField(max_length=255, blank=True, null=True)
    sms_description = models.CharField(max_length=255, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    email_description = models.CharField(max_length=255, blank=True, null=True)

    default_language = models.CharField(
        max_length=5, choices=settings.LANGUAGES, default="en"
    )

    location_country = models.CharField(
        max_length=5, choices=settings.COUNTRIES_N_CODES, default="en"
    )

    radiovis_enabled = models.BooleanField(default=False)
    radiovis_service = models.CharField(max_length=255, blank=True)
    radioepg_enabled = models.BooleanField(default=False, blank=True)
    radioepgpi_enabled = models.BooleanField(default=False)
    radioepg_service = models.CharField(max_length=255, blank=True)
    radiotag_enabled = models.BooleanField(default=False)
    radiotag_service = models.CharField(max_length=255, blank=True)
    radiospi_enabled = models.BooleanField(default=False)
    radiospi_service = models.CharField(max_length=255, blank=True, null=True)

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    default_image = models.ForeignKey(LogoImage, on_delete=models.CASCADE, blank=True, null=True)

    ip_allowed = models.CharField(max_length=256, blank=True, null=True)  # A list of ip/subnet, with , between
    genres = models.TextField(blank=True, null=True)

    @classmethod
    def all_stations_in_organization(cls, organization_id):
        return cls.objects.filter(organization__id=organization_id)
