from utils import get_db
import dns.resolver
import string
import random

db = get_db()


def to_json(inst, cls, bonusProps=[]):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    # add your coversions for things like datetime's 
    # and what-not that aren't serializable.
    d = dict()
    for c in cls.__table__.columns:
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
    random_password = db.Column(db.String(32))

    channels = db.relationship('Channel', backref='station', lazy='dynamic')


    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Station %r[%s]>' % (self.name, self.orga)

    def gen_random_password(self):
        self.random_password = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))

    @property
    def stomp_username(self):
        return str(self.id) + '.' + filter(lambda x: x in string.ascii_letters, self.name.lower())

    @property
    def json(self):
        return to_json(self, self.__class__, ['stomp_username'])


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

    def __repr__(self):
        return '<Channel %r[%s]>' % (self.name, self.station.__repr__)

    @property
    def topic(self):
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
                            cc_obj = Ecc.query.filter_by(id = value).first()
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
        return to_json(self, self.__class__, ['topic', 'radiodns_entry', 'station_name', 'default_picture_data'])

    @property
    def dns_values(self):
        fqdn = ''
        vis = ''
        epg = ''

        dns_entry = self.radiodns_entry

        # Special case with *
        if dns_entry[0] == '*':
            dns_entry = '10800' + dns_entry[1:]

        try:
            fqdn = str(dns.resolver.query(dns_entry, 'CNAME')[0])
            vis = str(dns.resolver.query('_radiovis._tcp.' + fqdn, 'SRV')[0])
            epg = str(dns.resolver.query('_radioepg._tcp.' + fqdn, 'SRV')[0])

        except dns.resolver.NXDOMAIN:
            pass

        return (fqdn, vis, epg)

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