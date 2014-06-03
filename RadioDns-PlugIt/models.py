from plugit import db
import dns.resolver
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


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    name = db.Column(db.String(80))
    short_name = db.Column(db.String(8))
    random_password = db.Column(db.String(32))

    ip_allowed = db.Column(db.String(256))  # A list of ip/subnet, with , between

    short_description = db.Column(db.String(180))

    genres = db.Column(db.Text())

    channels = db.relationship('Channel', backref='station', lazy='dynamic')
    shows = db.relationship('Show', backref='station', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='station', lazy='dynamic')
    servicefollowingentries = db.relationship('GenericServiceFollowingEntry', backref='station', lazy='dynamic')

    epg_picture_id = db.Column(db.Integer, db.ForeignKey('picture_forEPG.id'))

    @property
    def genres_list(self):
        try:
            return json.loads(self.genres)
        except:
            return []

    @property
    def epg_picture_data(self):
        if self.epg_picture:
            return self.epg_picture.json
        else:
            return None

    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Station %r[%s]>' % (self.name, self.orga)

    def gen_random_password(self):
        self.random_password = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))

    @property
    def short_name_to_use(self):
        """Return the shortname, based on the name or the short one"""
        return (self.short_name or self.name)[:8]

    @property
    def stomp_username(self):
        return str(self.id) + '.' + filter(lambda x: x in string.ascii_letters, self.name.lower())

    @property
    def json(self):
        return to_json(self, self.__class__, ['stomp_username', 'short_name_to_use', 'epg_picture_data', 'genres_list'])


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

        return (fqdn, vis, epg)

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
    def json(self):
        return to_json(self, self.__class__, ['clean_filename'])


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

    stations = db.relationship('Station', backref='epg_picture', lazy='dynamic')

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
