from django.conf import settings
from django.db import models

from apps.awsutils import awsutils
from apps.localization.models import Ecc, Language


class Organization(models.Model):
    codops = models.CharField(max_length=255)

    short_name = models.CharField(max_length=8)
    medium_name = models.CharField(max_length=16)
    long_name = models.CharField(max_length=128)
    short_description = models.CharField(max_length=180)
    long_description = models.CharField(max_length=1200, blank=True, null=True)
    url_default = models.URLField()

    postal_name = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=25, blank=True, null=True)
    phone_number = models.CharField(max_length=128, blank=True, null=True)

    default_language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, blank=True, null=True
    )
    location_country = models.ForeignKey(
        Ecc, on_delete=models.SET_NULL, blank=True, null=True
    )

    default_image_id = models.IntegerField(blank=True, null=True)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{self.medium_name}"

    def check_aws(self):
        return awsutils.check_serviceprovider(self)

    def escape_slash_rfc3986(self, value):
        if value:
            return value.replace("/", "%2F")
        return ""

    @property
    def epg_postal(self):
        if self.postal_name:
            return "postal:%s/%s/%s/%s/%s" % (
                self.escape_slash_rfc3986(self.postal_name),
                self.escape_slash_rfc3986(self.street),
                self.escape_slash_rfc3986(self.city),
                self.escape_slash_rfc3986(self.zipcode),
                self.escape_slash_rfc3986(self.location_country.name),
            )
        return None

    @property
    def epg_phone_number(self):
        if self.phone_number:
            return f"tel:{self.phone_number}"
        return None

    @property
    def fqdn(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.DOMAIN}"
        return None

    @property
    def vis_fqdn(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOVIS_DNS}"
        return None

    @property
    def epg_fqdn(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOEPG_DNS}"
        return None

    @property
    def spi_fqdn(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOSPI_DNS}"
        return None

    @property
    def tag_fqdn(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOTAG_DNS}"
        return None

    @property
    def vis_service(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOVIS_SERVICE_DEFAULT}"
        return None

    @property
    def epg_service(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOEPG_SERVICE_DEFAULT}"
        return None

    @property
    def tag_service(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOTAG_SERVICE_DEFAULT}"
        return None

    @property
    def spi_service(self):
        if self.codops:
            return f"{self.codops.lower()}.{settings.RADIOSPI_SERVICE_DEFAULT}"
        return None


class LogoImage(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    file = models.ImageField(blank=True, null=True)
    scaled32x32 = models.ImageField(blank=True, null=True)
    scaled112x32 = models.ImageField(blank=True, null=True)
    scaled128x128 = models.ImageField(blank=True, null=True)
    scaled320x240 = models.ImageField(blank=True, null=True)
    scaled600x600 = models.ImageField(blank=True, null=True)
