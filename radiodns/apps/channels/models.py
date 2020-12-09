from django.db import models
import dns.resolver

from apps.localization.models import Ecc
from apps.manager.models import Organization
from apps.stations.models import Station


class Image(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    file = models.ImageField(blank=True, null=True)
    radiotext = models.CharField(max_length=255)
    radiolink = models.URLField()


class Channel(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    TYPE_ID_CHOICES = [
        ("fm", "VHF/FM", ["ecc_id", "pi", "frequency"]),
        (
            "dab",
            "DAB",
            ["ecc_id", "eid", "sid", "scids", "appty_uatype", "pa", "mime_type"],
        ),
        ("drm", "DRM", ["sid"]),
        ("amss", "AMSS", ["sid"]),
        ("hd", "HD Radio", ["cc", "tx", "mid"]),
        (
            "id",
            "IP",
            ["fqdn", "serviceIdentifier", "stream_url", "mime_type", "bitrate"],
        ),
    ]
    TO_IGNORE_IN_DNS = ["stream_url", "mime_type", "bitrate"]

    type_id = models.CharField(max_length=5)

    # FM
    pi = models.CharField(max_length=4, blank=True, null=True)
    frequency = models.CharField(max_length=5, blank=True, null=True)

    # DAB/DAB+
    eid = models.CharField(max_length=4, blank=True, null=True)
    sid = models.CharField(max_length=8, blank=True, null=True)
    scids = models.CharField(max_length=3, blank=True, null=True)
    appty_uatype = models.CharField(max_length=6, blank=True, null=True)
    pa = models.IntegerField(blank=True, null=True)

    # IP
    stream_url = models.CharField(max_length=255, blank=True, null=True)
    bitrate = models.IntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=64, blank=True, null=True)

    # hd
    tx = models.CharField(max_length=5, blank=True, null=True)
    mid = models.IntegerField(blank=True, null=True)

    # ID
    fqdn = models.CharField(max_length=255, blank=True, null=True)
    serviceIdentifier = models.CharField(max_length=16, blank=True, null=True)

    default_image = models.ForeignKey(
        Image, on_delete=models.SET_NULL, blank=True, null=True
    )
    ecc = models.ForeignKey(Ecc, on_delete=models.SET_NULL, blank=True, null=True)

    def updateservicefollowingentry(self):
        """Updates the existing service following entry linked to the channel if one"""
        entries = self.genericservicefollowingentry_set.all()
        for entry in entries:
            if self.type_id == "dab" and not self.mime_type:
                entry.mime_type = "audio/mpeg"
            else:
                entry.mime_type = self.mime_type
            if self.type_id == "id" and not self.mime_type:
                entry.mime_type = "audio/mpeg"
            else:
                entry.mime_type = self.mime_type
            if self.type_id == "id" and not self.bitrate:
                entry.bitrate = 128
            else:
                entry.bitrate = self.bitrate
        entries.save()

    @property
    def service_identifier(self):
        gcc = self.ecc.pi + self.ecc.ecc
        if self.type_id == "fm":
            return "fm/{}/{}/{}".format(gcc, self.pi, self.frequency)
        elif self.type_id == "dab":
            return "dab/{}/{}/{}/{}".format(gcc, self.eid, self.sid, self.scids)

    @property
    def topic(self):
        return self.topic_no_slash + "/"

    @property
    def topic_no_slash(self):
        return "/topic/" + "/".join(self.dns_entry.split(".")[::-1])

    def generate_dns_entry(self, return_iso):
        val = self.type_id
        for (t, _, props) in Channel.TYPE_ID_CHOICES:
            if t == self.type_id:
                for v in props:
                    if getattr(self, v) is not None:
                        value = str(getattr(self, v)).lower()

                        if v == "ecc_id":  # Special case
                            if return_iso:
                                value = self.ecc.iso.lower()
                            else:
                                value = (self.ecc.pi + self.ecc.ecc).lower()

                        # Exclude certain parameters from the RadioDNS FQDN construction
                        if v in Channel.TO_IGNORE_IN_DNS:
                            continue
                        if v == "mid" and value == "1":
                            continue
                        val = value + "." + val
        return val

    @property
    def dns_entry(self):
        return self.generate_dns_entry(False)

    @property
    def dns_entry_iso(self):
        return self.generate_dns_entry(True)

    @property
    def radiodns_entry(self):
        return self.dns_entry + ".radiodns.org."

    @property
    def station_name(self):
        if self.station:
            return self.station.name
        else:
            return ""

    @property
    def station_ascii_name(self):
        if self.station:
            return self.station.default_instance.ascii_name.decode()
        else:
            return ""

    @property
    def dns_values(self):
        fqdn = ""
        vis = ""
        epg = ""
        tag = ""

        dns_entry = self.radiodns_entry

        # Special case with *
        if dns_entry[0] == "*":
            dns_entry = "10800" + dns_entry[1:]

        # Find radiodns servers
        ns = str(dns.resolver.query("radiodns.org", "NS")[0])
        ip = str(dns.resolver.query(ns, "A")[0])

        # Build a resolver using radiodns.org nameserver, timeout of 2, to be sure to have the latested FQDN
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 2  # Timeout of 2
        resolver.nameservers = [ip]  # Use radiodns.org servers

        try:
            fqdn = str(resolver.query(dns_entry, "CNAME")[0])
        except:
            pass
        else:
            try:
                vis = str(resolver.query("_radiovis._tcp." + fqdn, "SRV")[0])
            except:
                pass

            try:
                epg = str(resolver.query("_radioepg._tcp." + fqdn, "SRV")[0])
            except:
                pass

            try:
                tag = str(resolver.query("_radiotag._tcp." + fqdn, "SRV")[0])
            except:
                pass

        return fqdn, vis, epg, tag

    @property
    def epg_uri(self):

        # Special Case Urls / Streaming / Ip / Ids
        if self.type_id == "id" and self.stream_url:
            return self.stream_url

        splited = self.dns_entry.split(".")
        return splited[-1] + ":" + ".".join(splited[::-1][1:])
