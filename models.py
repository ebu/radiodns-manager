from utils import get_db
import json

db = get_db()

def to_json(inst, cls):
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
    return d

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orga = db.Column(db.Integer)
    name = db.Column(db.String(80))

    def __init__(self, orga):
        self.orga = orga

    def __repr__(self):
        return '<Station %r[%s]>' % (self.name, self.orga)

    @property
    def json(self):
        return to_json(self, self.__class__)