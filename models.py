from utils import get_db

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

    channels = db.relationship('Channel', backref='station', lazy='dynamic')


    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Station %r[%s]>' % (self.name, self.orga)

    @property
    def json(self):
        return to_json(self, self.__class__)


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

    TYPE_ID_CHOICES = [('fm', 'VHF/FM'), ('dab', 'DAB'), ('drm', 'DRM'), ('amss', 'AMSS'), ('hd', 'HD Radio'), ('id', 'IP')]

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

    def __repr__(self):
        return '<Channel %r[%s]>' % (self.name, self.station.__repr__)

    @property
    def radiodns_entry(self):
        return "!"

    @property
    def station_name(self):
        return self.station.name

    @property
    def json(self):
        return to_json(self, self.__class__, ['radiodns_entry', 'station_name'])