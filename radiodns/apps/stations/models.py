import json
import random
import string

import unicodedata
from urllib import parse
from django.db import models

from apps.awsutils import awsutils
from apps.clients.models import Client
from apps.localization.models import Ecc, Language
from apps.manager.models import Organization, LogoImage


class Station(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    default_image = models.ForeignKey(
        LogoImage, on_delete=models.SET_NULL, blank=True, null=True
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

    ip_allowed = models.CharField(
        max_length=256, blank=True, null=True
    )  # A list of ip/subnet, with , between

    @property
    def default_instance(self):
        return self.stationinstance_set.filter(client=None).first()

    @classmethod
    def all_stations_in_organization(cls, organization_id):
        return cls.objects.filter(organization__id=organization_id)


class StationInstance(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
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

    default_language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, blank=True, null=True
    )
    location_country = models.ForeignKey(
        Ecc, on_delete=models.SET_NULL, blank=True, null=True
    )

    genres = models.TextField(blank=True, null=True)

    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)

    def escape_slash_rfc3986(self, value):
        if value:
            return value.replace("/", "%2F")
        return None

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
    def epg_email(self):
        if self.email_address:
            return f"mailto:{self.email_address}"
        return None

    @property
    def epg_sms(self):
        if self.sms_body:
            if self.sms_body:
                return (
                    f"sms:{self.sms_number}?{parse.urlencode({'body': self.sms_body})}"
                )
            else:
                return "sms:{self.sms_number}"
        return None

    @property
    def genres_list(self):
        try:
            return json.loads(self.genres)
        except:
            return []

    @property
    def service_identifier(self):
        if self.station.organization:
            if self.station.organization.codops:
                return f"ebu{self.id}{self.station.organization.codops.lower()}"
        return None

    @property
    def ascii_name(self):
        return unicodedata.normalize("NFKD", self.name if self.name else "").encode(
            "ascii", "ignore"
        )

    def gen_random_password(self):
        self.random_password = "".join(
            random.choice(string.ascii_letters + string.digits) for x in range(32)
        )

    def check_aws(self):
        return awsutils.check_station(self)

    @property
    def short_name_to_use(self):
        """Return the shortname, based on the name or the short one"""
        return (
            (self.short_name or self.name)[:8] if self.short_name or self.name else ""
        )

    @property
    def fqdn_prefix(self):
        return "".join(
            filter(
                lambda x: x in string.ascii_letters + string.digits,
                self.ascii_name.decode("ascii").lower(),
            )
        )

    @property
    def fqdn(self):
        if self.station.organization:
            return "%s.%s" % (self.fqdn_prefix, self.station.organization.fqdn)
        return None

    @property
    def stomp_username(self):
        return (
            str(self.id)
            + "."
            + "".join(
                filter(
                    lambda x: x in string.ascii_letters + string.digits,
                    self.ascii_name.decode("ascii").lower(),
                )
            )
        )
