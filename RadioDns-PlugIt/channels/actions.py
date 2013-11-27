# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile

from models import db, Station, Channel, Ecc

import re

import config

from plugit.api import PlugItAPI

import StringIO


@action(route="/channels/", template="channels/home.html")
@only_orga_member_user()
def channels_home(request):
    """Show the list of channels."""

    list = []

    for elem in Channel.query.join(Station).filter(Station.orga==int(request.args.get('ebuio_orgapk'))).order_by(Channel.name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    
    return {'list': list, 'saved': saved, 'deleted': deleted}


@action(route="/channels/edit/<id>", template="channels/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def channels_edit(request, id):
    """Edit a channel."""

    object = None
    errors = []

    if id != '-':
        object = Channel.query.join(Station).filter(Channel.id == int(id), Station.orga==int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))).first()

    if request.method == 'POST':

        if not object:
            object = Channel()


        object.station_id = int(request.form.get('station'))

        # Get values
        for x in ['name', 'type_id', 'ecc_id', 'pi', 'frequency', 'eid', 'sid', 'scids', 'appty_uatype', 'pa', 'tx', 'cc', 'fqdn', 'serviceIdentifier']:
            val = request.form.get(x)
            if val == '':
                val = None

            # Secial case : CC
            if x == 'cc' and val is not None:
                cc_obj = Ecc.query.filter_by(id = val).first()
                val = cc_obj.pi + cc_obj.ecc


            setattr(object, x, val)

        # Check errors
        if object.name == '' or object.name is None:
            errors.append("Please set a name")

        # Set to '' useless values, and check if values needed are present
        list_props = None
        for (type_id, _, type_props) in Channel.TYPE_ID_CHOICES:
            if type_id == object.type_id:
                list_props = type_props

        if list_props is None:
            errors.append('Type not found oO')

        if list_props:

            for x in ['ecc_id', 'pi', 'frequency', 'eid', 'sid', 'scids', 'appty_uatype', 'pa', 'tx', 'cc', 'fqdn', 'serviceIdentifier']:
                if x in list_props:  # Want it ? Keep it !
                    if x != 'appty_uatype' and x != 'pa':  # Exception
                        if getattr(object, x) is None or getattr(object, x) == '':
                            errors.append(x + " cannot be empty")
                else:
                    setattr(object, x, None)

        # Check each prop
        if object.pi is not None:
            if not re.match(r"^[a-fA-F0-9]{4}$", object.pi):
                errors.append("pi must be 4 characters in hexadecimal")

        if object.frequency is not None:
            if not re.match(r"^[0-9]{5}$", object.frequency) and object.frequency != '*':
                errors.append("frequency must be 5 digits or *")

        if object.eid is not None:
            if not re.match(r"^[a-fA-F0-9]{4}$", object.eid):
                errors.append("eid must be 4 characters in hexadecimal")

        if object.sid is not None:
            if not re.match(r"^[a-fA-F0-9]{4}([a-fA-F0-9]{4})?$", object.sid):
                errors.append("sid must be 4 or 8 characters in hexadecimal")

        if object.scids is not None:
            if not re.match(r"^[a-fA-F0-9]([a-fA-F0-9]{2})?$", object.scids):
                errors.append("scids must be 1 or 3 characters in hexadecimal")

        if object.appty_uatype is not None:
            if not re.match(r"^[a-fA-F0-9]{2}\-[a-fA-F0-9]{3}$", object.appty_uatype):
                errors.append("appty_uatype must be 2 char hexadecimal, hyphen, 3 char hexadecimal")

        if object.pa is not None:
            if object.pa < 1 or object.pa > 1023:
                errors.append("pa must be between 1 and 1023")

        if object.tx is not None:
            if not re.match(r"^[a-fA-F0-9]{5}$", object.tx):
                errors.append("tx must be 5 characters in hexadecimal")

        if object.cc is not None:
            if not re.match(r"^[a-fA-F0-9]{3}$", object.cc):
                errors.append("cc must be 3 characters in hexadecimal")

        if object.fqdn is not None:
            if not re.match(r"^[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63}).$", object.fqdn):
                errors.append("fqdn must be a domain name")

        if object.serviceIdentifier is not None:
            if not re.match(r"^[a-f0-9]{,16}$", object.serviceIdentifier):
                errors.append("serviceIdentifier must be up to 16 characters in hexadecimal, lowercase")



        # Check station
        sta = Station.query.filter_by(id=object.station_id).first()
        if not sta or sta.orga != int(request.form.get('ebuio_orgapk')):
            errors.append("Please set a station")

        # If no errors, save
        if not errors:
            
            if not object.id:
                db.session.add(object)

            db.session.commit()

            return PlugItRedirect('channels/?saved=yes')

    if object:
        object = object.json

    stations = []

    for station in Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))).all():
        stations.append(station.json)
       
    return {'object': object, 'errors': errors, 'stations': stations, 'types_id': Channel.TYPE_ID_CHOICES}

@action(route="/channels/delete/<id>")
@json_only()
@only_orga_admin_user()
def channels_delete(request, id):
    """Delete a channel."""

    object = Channel.query.join(Station).filter(Channel.id == int(id), Station.orga==int(request.args.get('ebuio_orgapk'))).first()

    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('channels/?deleted=yes')

@action(route="/channels/check/<id>")
@json_only()
@only_orga_member_user()
def channels_check(request, id):
    """Check (and return DNS info) about a channel."""

    object = Channel.query.join(Station).filter(Channel.id == int(id), Station.orga==int(request.args.get('ebuio_orgapk'))).first()

    (fqdn, vis, epg) = object.dns_values

    return {'dns': object.radiodns_entry, 'fqdn': fqdn, 'vis': vis, 'epg': epg}


@action(route="/channels/export/", template="channels/export.html")
@only_orga_member_user()
def channels_export(request):
    """Export channels to zone file."""

    plugitapi = PlugItAPI(config.API_URL)

    retour = ''

    retour += '; GENERATED BY EBU RADIOVISMANAGER\n'
    retour += '; http://ebu.io/plugit/1\n\n'
    retour += '; Organization ' + plugitapi.get_orga(request.args.get('ebuio_orgapk')).name + '\n\n'

    oldStationName = ''

    for elem in Channel.query.join(Station).filter(Station.orga==int(request.args.get('ebuio_orgapk'))).order_by(Station.name, Channel.name).all():
        if elem.station_name != oldStationName:
            retour += '\n;;; Station: ' + elem.station_name + '\n'
            oldStationName = elem.station_name

        retour += elem.dns_entry.ljust(40) + '\tIN\tCNAME\trdns.ebulabs.org.\n'

    if request.args.get('to') == 'file':
        retour_str = StringIO.StringIO()
        retour_str.write(str(retour))
        retour_str.seek(0)
        return PlugItSendFile(retour_str, 'text/plain', True, plugitapi.get_orga(request.args.get('ebuio_orgapk')).name + '-radiodns.org.zone')

    return {'retour': retour}