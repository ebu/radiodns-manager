from plugit import db
from aws import awsutils
import dns.resolver
import config
import string
import random
import datetime
import json


def to_json(inst, cls, bonusProps=[]):
    """
    Jsonify the sql alchemy query result.
    Inspired from http://stackoverflow.com/a/9746249
    """
    convert = dict()
    # add your coversions for things like datetime's
    # and what-not that aren't serializable.
    d = dict()
    for c in cls.__table__.columns:
        if not hasattr(inst, c.name):  # If the field was inherited
            continue
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    for p in bonusProps:
        d[p] = getattr(inst, p)
    return d

class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codops = db.Column(db.String(255))

    short_name = db.Column(db.String(8))
    medium_name = db.Column(db.String(16))
    long_name = db.Column(db.String(128))
    short_description = db.Column(db.String(180))
    long_description = db.Column(db.String(1200))
    url_default = db.Column(db.String(255))

    default_language = db.Column(db.String(5))

    location_country = db.Column(db.String(5))

    default_logo_image_id = db.Column(db.Integer, db.ForeignKey('logo_image.id', use_alter=True, name='fk_default_logo_id'))
    default_logo_image = db.relationship("LogoImage", foreign_keys=[default_logo_image_id])

    stations = db.relationship('Station', backref='service_provider', lazy='dynamic')

    def __init__(self, codops):
        self.codops = codops

    def __repr__(self):
         return '<ServiceProvider %r[%s]>' % (self.short_name, self.codops)

    def check_aws(self):
        return awsutils.check_serviceprovider(self)

    @property
    def default_logo_image_data(self):
        if self.default_logo_image:
            return self.default_logo_image.json
        else:
            return None

    @property
    def fqdn(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.DOMAIN)
        return None

    @property
    def vis_fqdn(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.RADIOVIS_DNS)
        return None

    @property
    def epg_fqdn(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.RADIOEPG_DNS)
        return None

    @property
    def tag_fqdn(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.RADIOTAG_DNS)
        return None

    @property
    def vis_service(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.RADIOVIS_SERVICE_DEFAULT)
        return None

    @property
    def epg_service(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.RADIOEPG_SERVICE_DEFAULT)
        return None

    @property
    def tag_service(self):
        if self.codops:
            return "%s.%s" % (self.codops.lower(), config.RADIOTAG_SERVICE_DEFAULT)
        return None

    @property
    def image_url_prefix(self):
        return awsutils.get_public_urlprefix(self)

    @property
    def json(self):
        return to_json(self, self.__class__, ['default_logo_image_data', 'image_url_prefix', 'fqdn',
                                              'vis_fqdn', 'epg_fqdn', 'tag_fqdn',
                                              'vis_service', 'epg_service', 'tag_service'])


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    name = db.Column(db.String(80))
    short_name = db.Column(db.String(8))
    medium_name = db.Column(db.String(16))
    long_name = db.Column(db.String(128))
    short_description = db.Column(db.String(180))
    long_description = db.Column(db.String(1200))
    url_default = db.Column(db.String(255))
    random_password = db.Column(db.String(32))

    # Services
    #fqdn_station_prefix = db.Column(db.String(255)) maybe to add due to filtering issue in Alchemy
    radiovis_enabled = db.Column(db.Boolean)
    radiovis_service = db.Column(db.String(255))
    radioepg_enabled = db.Column(db.Boolean)
    radioepg_service = db.Column(db.String(255))
    radiotag_enabled = db.Column(db.Boolean)
    radiotag_service = db.Column(db.String(255))

    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'))

    ip_allowed = db.Column(db.String(256))  # A list of ip/subnet, with , between

    short_description = db.Column(db.String(180))

    genres = db.Column(db.Text())

    channels = db.relationship('Channel', backref='station', lazy='dynamic')
    shows = db.relationship('Show', backref='station', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='station', lazy='dynamic')
    servicefollowingentries = db.relationship('GenericServiceFollowingEntry', backref='station', lazy='dynamic')

    #epg_picture_id = db.Column(db.Integer, db.ForeignKey('picture_forEPG.id'))
    default_logo_image_id = db.Column(db.Integer, db.ForeignKey('logo_image.id', use_alter=True, name='fk_epg_default_logo_id'))
    default_logo_image = db.relationship("LogoImage", foreign_keys=[default_logo_image_id])

    @property
    def service_provider_data(self):
        if self.service_provider:
            return self.service_provider.json
        else:
            return None

    @property
    def genres_list(self):
        try:
            return json.loads(self.genres)
        except:
            return []

    @property
    def default_logo_image_data(self):
        if self.default_logo_image:
            return self.default_logo_image.json
        else:
            return None

    @property
    def fqdn(self):
        if self.service_provider:
            if self.service_provider.codops:
                return "%s.%s.%s" % (filter(lambda x: x in string.ascii_letters + string.digits, self.name.lower()),
                                     self.service_provider.codops.lower(), config.DOMAIN)
        return None



    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Station %r[%s]>' % (self.name, self.orga)

    def gen_random_password(self):
        self.random_password = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))

    def check_aws(self):
        return awsutils.check_station(self)

    @property
    def short_name_to_use(self):
        """Return the shortname, based on the name or the short one"""
        return (self.short_name or self.name)[:8]

    @property
    def fqdn_prefix(self):
        return filter(lambda x: x in string.ascii_letters + string.digits, self.name.lower())

    @property
    def fqdn(self):
        if self.service_provider:
            return "%s.%s" % (self.fqdn_prefix, self.service_provider.fqdn)
        return None

    @property
    def stomp_username(self):
        return str(self.id) + '.' + filter(lambda x: x in string.ascii_letters , self.name.lower()) # + string.digits

    @property
    def json(self):
        return to_json(self, self.__class__, ['stomp_username', 'short_name_to_use', 'service_provider_data', 'default_logo_image_data', 'genres_list',
                                              'fqdn', 'fqdn_prefix'])


class Ecc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    iso = db.Column(db.String(2))
    pi = db.Column(db.String(2))
    ecc = db.Column(db.String(3))

    def __repr__(self):
        return '<Ecc %r>' % self.name

    @property
    def json(self):
        return to_json(self, self.__class__)


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    name = db.Column(db.String(255))

    TYPE_ID_CHOICES = [ ('fm',   'VHF/FM',    ['ecc_id', 'pi', 'frequency']),
                        ('dab',  'DAB',       ['ecc_id', 'eid', 'sid', 'scids', 'appty_uatype', 'pa']),
                        ('drm',  'DRM',       ['sid']),
                        ('amss', 'AMSS',      ['sid']),
                        ('hd',   'HD Radio',  ['cc', 'tx']),
                        ('id',   'IP',        ['fqdn', 'serviceIdentifier'])
                        ]

    type_id = db.Column(db.String(5))

    ecc_id = db.Column(db.Integer, db.ForeignKey('ecc.id'))

    pi = db.Column(db.String(4))
    frequency = db.Column(db.String(5))

    eid = db.Column(db.String(4))
    sid = db.Column(db.String(8))
    scids = db.Column(db.String(3))

    appty_uatype = db.Column(db.String(6))
    pa = db.Column(db.Integer)

    tx = db.Column(db.String(5))
    cc = db.Column(db.String(3))

    fqdn = db.Column(db.String(255))
    serviceIdentifier = db.Column(db.String(16))

    default_picture_id = db.Column(db.Integer, db.ForeignKey('picture.id'))

    servicefollowingentries = db.relationship('GenericServiceFollowingEntry', backref='channel', lazy='dynamic')

    def __repr__(self):
        return '<Channel %r[%s]>' % (self.name, self.station.__repr__)

    @property
    def servicefollowingentry(self):
        """Return (or create) the associated service following entry"""

        # Find in exisiting objects
        entries = self.servicefollowingentries.all()
        if len(entries) > 0:
            return entries[0]

        # Create a new one

        object = GenericServiceFollowingEntry()
        object.channel_id = self.id
        object.active = False
        object.cost = 100
        object.offset = 0

        if self.type_id == 'dab':
            object.mime_type = 'audio/mpeg'
        else:
            object.mime_type = ''

        db.session.add(object)
        db.session.commit()

        return object

    @property
    def topic(self):
        return '/topic/' + '/'.join(self.dns_entry.split('.')[::-1]) + '/'

    @property
    def topic_no_slash(self):
        return '/topic/' + '/'.join(self.dns_entry.split('.')[::-1])

    @property
    def dns_entry(self):
        val = self.type_id
        for (t, _, props) in Channel.TYPE_ID_CHOICES:
            if t == self.type_id:
                for v in props:
                    if getattr(self, v) is not None:
                        value = str(getattr(self, v)).lower()

                        if v == 'ecc_id':  # Special case
                            cc_obj = Ecc.query.filter_by(id=value).first()
                            value = (cc_obj.pi + cc_obj.ecc).lower()

                        val = value + '.' + val
        return val

    @property
    def dns_entry_iso(self):
        val = self.type_id
        for (t, _, props) in Channel.TYPE_ID_CHOICES:
            if t == self.type_id:
                for v in props:
                    if getattr(self, v) is not None:
                        value = str(getattr(self, v)).lower()

                        if v == 'ecc_id':  # Special case
                            cc_obj = Ecc.query.filter_by(id=value).first()
                            value = (cc_obj.iso).lower()

                        val = value + '.' + val
        return val

    @property
    def radiodns_entry(self):
        return self.dns_entry + '.radiodns.org.'

    @property
    def station_name(self):
        if self.station:
            return self.station.name
        else:
            return ''

    @property
    def default_picture_data(self):
        if self.default_picture:
            return self.default_picture.json
        else:
            return None

    @property
    def json(self):
        return to_json(self, self.__class__, ['topic', 'radiodns_entry', 'station_name', 'default_picture_data', 'topic_no_slash'])

    @property
    def dns_values(self):
        fqdn = ''
        vis = ''
        epg = ''
        tag = ''

        dns_entry = self.radiodns_entry

        # Special case with *
        if dns_entry[0] == '*':
            dns_entry = '10800' + dns_entry[1:]

        # Find radiodns servers
        ns = str(dns.resolver.query('radiodns.org', 'NS')[0])
        ip = str(dns.resolver.query(ns, 'A')[0])

        # Build a resolver using radiodns.org nameserver, timeout of 2, to be sure to have the latested FQDN
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 2  # Timeout of 2
        resolver.nameservers = [ip]  # Use radiodns.org servers

        try:
            fqdn = str(resolver.query(dns_entry, 'CNAME')[0])
        except:
            pass

        # Build resolver for others queries using local nameserver
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 2  # Timeout of 2

        if fqdn:
            try:
                vis = str(resolver.query('_radiovis._tcp.' + fqdn, 'SRV')[0])
            except:
                pass

            try:
                epg = str(resolver.query('_radioepg._tcp.' + fqdn, 'SRV')[0])
            except:
                pass

            try:
                tag = str(resolver.query('_radiotag._tcp.' + fqdn, 'SRV')[0])
            except:
                pass

        return (fqdn, vis, epg, tag)

    @property
    def epg_uri(self):
        splited = self.dns_entry.split('.')
        return splited[-1] + ':' + '.'.join(splited[::-1][1:])


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    name = db.Column(db.String(80))
    filename = db.Column(db.String(255))
    radiotext = db.Column(db.String(255))
    radiolink = db.Column(db.String(255))
    image_url_prefix = db.Column(db.String(255))

    channels = db.relationship('Channel', backref='default_picture', lazy='dynamic')

    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Picture %r[%s]>' % (self.name, self.orga)

    @property
    def clean_filename(self):
        if not self.filename:
            return ''

        return self.filename.split('/')[-1]

    @property
    def public_url(self):
        return "%s%s" % (self.image_url_prefix, self.filename)

    @property
    def json(self):
        return to_json(self, self.__class__, ['clean_filename', 'public_url'])


class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255))
    body = db.Column(db.Text())
    headers = db.Column(db.Text())
    reception_timestamp = db.Column(db.Integer())

    @property
    def reception_date(self):
        return datetime.datetime.fromtimestamp(self.reception_timestamp)

    @property
    def json(self):
        return to_json(self, self.__class__, ['reception_date'])


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    medium_name = db.Column(db.String(255))
    long_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    color = db.Column(db.String(7))

    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))

    schedules = db.relationship('Schedule', backref='show', lazy='dynamic')

    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Show %r[%s]>' % (self.medium_name, self.orga)

    @property
    def json(self):
        return to_json(self, self.__class__, [])


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))

    day = db.Column(db.Integer)
    start_hour = db.Column(db.Integer)
    start_minute = db.Column(db.Integer)
    length = db.Column(db.Integer)

    @property
    def seconds_from_base(self):
        """The number, in seconds of start, based on monday 00:00"""
        return self.day * 24 * 60 * 60 + self.start_hour * 60 * 60 + self.start_minute * 60

    @property
    def duration(self):

        return 'PT' + str(int(self.length / 60)) + 'H' + str(self.length % 60) + 'M'

    @property
    def date_of_start_time(self):
        """Return the start time as a date, assuming start_date has been set as a reference"""
        import datetime
        return (self.start_date + datetime.timedelta(days=self.day, hours=self.start_hour, minutes=self.start_minute))

    @property
    def start_time(self):
        """Return the start time as a string, assuming start_date has been set as a reference"""
        timetime_format = '%Y-%m-%dT%H:%M:%S%z'

        if not hasattr(self, 'start_date'):
            return ''

        return self.date_of_start_time.strftime(timetime_format)

    @property
    def json_show(self):
        return self.show.json

    @property
    def json(self):
        return to_json(self, self.__class__, ['json_show', 'start_time', 'duration'])


class GenericServiceFollowingEntry(db.Model):
    """A generic entry for service following"""
    """If channel id is set, object is linked to a channel, otherwise station_id and channel_uri must be set, linking to a station"""

    id = db.Column(db.Integer, primary_key=True)

    active = db.Column(db.Boolean)
    cost = db.Column(db.Integer)
    offset = db.Column(db.Integer)
    mime_type = db.Column(db.String(255))

    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=True)

    station_id = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=True)
    channel_uri = db.Column(db.String(255), nullable=True)

    @property
    def channel_name(self):
        """The name of the channel, if linked to a channel"""
        if self.channel:
            return self.channel.name
        return ''

    @property
    def channel_type(self):
        """The type of the channel, if linked to a channel"""
        if self.channel:
            return self.channel.type_id
        return ''

    @property
    def uri(self):
        """The uri to use"""
        if self.channel:
            return self.channel.epg_uri
        else:
            return self.channel_uri

    @property
    def type(self):
        if self.channel:
            return 'channel'
        else:
            return 'ip'

    @property
    def json(self):
        return to_json(self, self.__class__, ['channel_name', 'uri', 'type', 'channel_type'])


class PictureForEPG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    name = db.Column(db.String(80))
    filename = db.Column(db.String(255))

    #stations = db.relationship('Station', backref='epg_picture', lazy='dynamic')

    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<PictureForEPG %r[%s]>' % (self.name, self.orga)

    @property
    def clean_filename(self):
        if not self.filename:
            return ''

        return self.filename.split('/')[-1]

    @property
    def json(self):
        return to_json(self, self.__class__, ['clean_filename'])


class LogoImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    codops = db.Column(db.String(255))

    name = db.Column(db.String(255))
    filename = db.Column(db.String(255))

    url32x32 = db.Column(db.String(255))
    url112x32 = db.Column(db.String(255))
    url128x128 = db.Column(db.String(255))
    url320x240 = db.Column(db.String(255))
    url600x600 = db.Column(db.String(255))

    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'))
    service_provider = db.relationship("ServiceProvider", backref='logo_images', uselist=False, foreign_keys=[service_provider_id])

    stations = db.relationship('Station', backref='epg_picture', lazy='dynamic')

    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<LogoImage %r[%s]>' % (self.filename, self.orga)

    @property
    def clean_filename(self):
        if not self.filename:
            return ''

        return self.filename.split('/')[-1]

    @property
    def public_url(self):
        if self.service_provider:
            return "%s%s" % (self.service_provider.image_url_prefix, self.filename)
        else:
            return None
    @property
    def public_32x32_url(self):
        if self.url32x32:
            return "%s%s" % (self.service_provider.image_url_prefix, self.url32x32)
        else:
            return self.public_url
    @property
    def public_112x32_url(self):
        if self.url112x32:
            return "%s%s" % (self.service_provider.image_url_prefix, self.url112x32)
        else:
            return self.public_url
    @property
    def public_128x128_url(self):
        if self.url128x128:
            return "%s%s" % (self.service_provider.image_url_prefix, self.url128x128)
        else:
            return self.public_url
    @property
    def public_320x240_url(self):
        if self.url320x240:
            return "%s%s" % (self.service_provider.image_url_prefix, self.url320x240)
        else:
            return self.public_url
    @property
    def public_600x600_url(self):
        if self.url600x600:
            return "%s%s" % (self.service_provider.image_url_prefix, self.url600x600)
        else:
            return self.public_url

    @property
    def json(self):
        return to_json(self, self.__class__, ['clean_filename', 'public_url',
                                              'public_32x32_url', 'public_112x32_url', 'public_128x128_url',
                                              'public_320x240_url', 'public_600x600_url'])