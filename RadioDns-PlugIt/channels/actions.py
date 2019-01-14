# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile

from models import db, Station, Channel, Ecc, ServiceProvider, Clients
import re

import config

from plugit.api import PlugItAPI

import StringIO

from stations.utils import gen_default_client


@action(route="/channels/", template="channels/home.html")
@only_orga_member_user()
def channels_home(request):
    """Show the list of channels."""

    plugitapi = PlugItAPI(config.API_URL)
    orga_id = request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')
    orga = plugitapi.get_orga(orga_id)

    expected_fqdn = 'radio.ebu.io'

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
        if sp:
            expected_fqdn = sp.fqdn

    list = []

    for elem in Channel.query.join(Station).filter(Station.orga == int(request.args.get('ebuio_orgapk'))).order_by(
            Station.name, Channel.type_id, Channel.name).all():
        list.append(elem.json)

    stations = []

    for station in Station.query.filter_by(
            orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))).all():
        stations.append(station.json)

    saved = request.args.get('saved') == 'yes'
    newchannelscount = request.args.get('newchannelscount')
    deleted = request.args.get('deleted') == 'yes'

    if sp:
        sp = sp.json

    return {'list': list, 'stations': stations, 'expected_fqdn': expected_fqdn,
            'serviceprovider': sp, 'ebu_codops': orga.codops,
            'saved': saved, 'deleted': deleted, 'newchannelscount': newchannelscount}


@action(route="/channels/edit/<id>", template="channels/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def channels_edit(request, id):
    """Edit a channel."""

    station = None
    channel = None
    errors = []

    station_id = request.args.get('station_id')
    if station_id:
        station = Station.query.filter(Station.id == station_id,
                                       Station.orga == int(request.args.get('ebuio_orgapk') or request.form.get(
                                           'ebuio_orgapk'))).first()

    if id != '-':
        channel = Channel.query.join(Station).filter(Channel.id == int(id),
                                                    Station.orga == int(
                                                        request.args.get('ebuio_orgapk') or request.form.get(
                                                            'ebuio_orgapk'))).first()

    if request.method == 'POST':

        if not channel:
            channel = Channel()

        channel.station_id = int(request.form.get('station'))

        # Get values
        for x in ['name', 'type_id', 'ecc_id', 'pi', 'frequency', 'eid', 'sid', 'scids', 'appty_uatype', 'pa', 'tx',
                  'cc', 'fqdn', 'stream_url', 'mime_type', 'bitrate', 'serviceIdentifier', 'fk_client']:
            val = request.form.get(x)
            if val == '':
                val = None

            # Secial case : CC
            if x == 'cc' and val is not None:
                cc_obj = Ecc.query.filter_by(id=val).first()
                val = cc_obj.pi + cc_obj.ecc

            setattr(channel, x, val)

        # Check errors
        if channel.name == '' or channel.name is None:
            errors.append("Please set a name")

        # Set to '' useless values, and check if values needed are present
        list_props = None
        for (type_id, _, type_props) in Channel.TYPE_ID_CHOICES:
            if type_id == channel.type_id:
                list_props = type_props

        if list_props is None:
            errors.append('Type not found!')

        if list_props:

            for x in ['ecc_id', 'pi', 'frequency', 'eid', 'sid', 'scids', 'appty_uatype', 'pa', 'tx', 'cc', 'fqdn',
                      'mime_type', 'stream_url', 'bitrate', 'serviceIdentifier']:
                if x in list_props:  # Want it ? Keep it !
                    if x != 'appty_uatype' and x != 'pa':  # Exception
                        if getattr(channel, x) is None or getattr(channel, x) == '':
                            errors.append(x + " cannot be empty")
                else:
                    setattr(channel, x, None)

        # Check each prop
        if channel.pi is not None:
            if not re.match(r"^[a-fA-F0-9]{4}$", channel.pi):
                errors.append("pi must be 4 characters in hexadecimal")

        if channel.frequency is not None:
            if not re.match(r"^[0-9]{5}$", channel.frequency) and channel.frequency != '*':
                errors.append("frequency must be 5 digits or *")

        if channel.eid is not None:
            if not re.match(r"^[a-fA-F0-9]{4}$", channel.eid):
                errors.append("eid must be 4 characters in hexadecimal")

        if channel.sid is not None:
            if not re.match(r"^[a-fA-F0-9]{4}([a-fA-F0-9]{4})?$", channel.sid):
                errors.append("sid must be 4 or 8 characters in hexadecimal")

        if channel.scids is not None:
            if not re.match(r"^[a-fA-F0-9]([a-fA-F0-9]{2})?$", channel.scids):
                errors.append("scids must be 1 or 3 characters in hexadecimal")

        if channel.appty_uatype is not None:
            if not re.match(r"^[a-fA-F0-9]{2}\-[a-fA-F0-9]{3}$", channel.appty_uatype):
                errors.append("appty_uatype must be 2 char hexadecimal, hyphen, 3 char hexadecimal")

        if channel.pa is not None:
            if channel.pa < 1 or channel.pa > 1023:
                errors.append("pa must be between 1 and 1023")

        if channel.tx is not None:
            if not re.match(r"^[a-fA-F0-9]{5}$", channel.tx):
                errors.append("tx must be 5 characters in hexadecimal")

        if channel.cc is not None:
            if not re.match(r"^[a-fA-F0-9]{3}$", channel.cc):
                errors.append("cc must be 3 characters in hexadecimal")

        if channel.fqdn is not None:
            channel.fqdn = channel.fqdn.rstrip('.')
            if not re.match(r"(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}\.?$)", channel.fqdn):
                errors.append("fqdn must be a domain name")

        if channel.serviceIdentifier is not None:
            if not re.match(r"^[a-z0-9]{,16}$", channel.serviceIdentifier):
                errors.append("serviceIdentifier must be up to 16 letters or number, lowercase")

        if channel.mime_type is not None:
            if not re.match(r"^([!-\.0-~]{1,}\/[!-\.0-~]{1,})+$", channel.mime_type):
                errors.append("mime_type must be of format string/string ")

        if channel.bitrate is not None:
            if not re.match(r"^[0-9]+$", channel.bitrate):
                errors.append("bitrate must be digits")

        # Check station
        sta = Station.query.filter_by(id=channel.station_id).first()
        if not sta or sta.orga != int(request.form.get('ebuio_orgapk')):
            errors.append("Please set a station")

        # If no errors, save
        if not errors:

            if not channel.id:
                db.session.add(channel)

            db.session.commit()

            # Update the service entries for the channel
            channel.updateservicefollowingentry()

            if station:
                return PlugItRedirect(('stations/%s/channels?saved=yes') % station.id)
            else:
                return PlugItRedirect('channels/?saved=yes')

    default_country = None

    plugitapi = PlugItAPI(config.API_URL)
    orga_id = request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')
    orga = plugitapi.get_orga(orga_id)
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
        if sp:
            cc_obj = Ecc.query.filter_by(iso=sp.location_country).first()
            if cc_obj:
                default_country = cc_obj.id

    if channel:
        channel = channel.json

    stations = []

    for s in Station.query.filter_by(
            orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')),
            parent=None
    ).all():
        stations.append(s.json)

    if station:
        station = station.json

    clients = [gen_default_client()] + Clients.query.filter_by(orga=orga_id).order_by(Clients.id).all()

    return {'object': channel, 'errors': errors, 'stations': stations, 'station': station,
            'types_id': Channel.TYPE_ID_CHOICES, 'default_country': default_country,
            'clients': map(lambda c: c.json, clients)
            }


@action(route="/channels/import", template="channels/import.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def channels_import(request):
    """Import a list of channel."""

    data = ''
    new_channels_count = 0
    global_errors = []
    error_lines = []

    if request.method == 'POST':

        # Get values
        data = request.form.get('importdata')
        station_id = int(request.form.get('station'))

        # Foreach Line
        for line in data.split("\n"):
            line = line.strip()
            if line:

                errors = []
                # Extract data
                object = string_to_channel(line, station_id)

                # Check errors
                if object is None:
                    errors.append("Could not convert text line to channel for line " + line)
                else:
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

                        for x in ['ecc_id', 'pi', 'frequency', 'eid', 'sid', 'scids', 'appty_uatype', 'pa', 'tx', 'cc',
                                  'fqdn', 'stream_url', 'mime_type', 'bitrate', 'serviceIdentifier']:
                            if x in list_props:  # Want it ? Keep it !
                                if x != 'appty_uatype' and x != 'pa':  # Exception
                                    if getattr(object, x) is None or getattr(object, x) == '':
                                        errors.append(x + " cannot be empty")
                            else:
                                setattr(object, x, None)

                    # Check each prop
                    if object.pi is not None:
                        if not re.match(r"^[a-fA-F0-9]{4}$", object.pi):
                            errors.append("pi must be 4 characters in hexadecimal for line " + line)

                    if object.frequency is not None:
                        if not re.match(r"^[0-9]{5}$", object.frequency) and object.frequency != '*':
                            errors.append("frequency must be 5 digits or *")

                    if object.eid is not None:
                        if not re.match(r"^[a-fA-F0-9]{4}$", object.eid):
                            errors.append("eid must be 4 characters in hexadecimal for line " + line)

                    if object.sid is not None:
                        if not re.match(r"^[a-fA-F0-9]{4}([a-fA-F0-9]{4})?$", object.sid):
                            errors.append("sid must be 4 or 8 characters in hexadecimal for line " + line)

                    if object.scids is not None:
                        if not re.match(r"^[a-fA-F0-9]([a-fA-F0-9]{2})?$", object.scids):
                            errors.append("scids must be 1 or 3 characters in hexadecimal for line " + line)

                    if object.appty_uatype is not None:
                        if not re.match(r"^[a-fA-F0-9]{2}\-[a-fA-F0-9]{3}$", object.appty_uatype):
                            errors.append(
                                "appty_uatype must be 2 char hexadecimal, hyphen, 3 char hexadecimal for line " + line)

                    if object.pa is not None:
                        if object.pa < 1 or object.pa > 1023:
                            errors.append("pa must be between 1 and 1023 for line " + line)

                    if object.tx is not None:
                        if not re.match(r"^[a-fA-F0-9]{5}$", object.tx):
                            errors.append("tx must be 5 characters in hexadecimal for line " + line)

                    if object.cc is not None:
                        if not re.match(r"^[a-fA-F0-9]{3}$", object.cc):
                            errors.append("cc must be 3 characters in hexadecimal for line " + line)

                    if object.fqdn is not None:
                        if not re.match(r"(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}\.?$)",
                                        object.fqdn):
                            errors.append("fqdn must be a domain name for line " + line)

                    if object.serviceIdentifier is not None:
                        if not re.match(r"^[a-z0-9]{,16}$", object.serviceIdentifier):
                            errors.append(
                                "serviceIdentifier must be up to 16 characters in hexadecimal, lowercase for line " + line)

                    if object.mime_type is not None:
                        if not re.match(r"^\w+\/\w+$", object.mime_type):
                            errors.append("mime_type must be of format string/string " + line)

                    if object.bitrate is not None:
                        if not re.match(r"^[0-9]+$", object.bitrate):
                            errors.append("bitrate must be digits")

                    # Check station
                    sta = Station.query.filter_by(id=object.station_id).first()
                    if not sta or sta.orga != int(request.form.get('ebuio_orgapk')):
                        errors.append("Please set a station")

                # If no errors, save
                if not errors:

                    if not object.id:
                        db.session.add(object)
                        new_channels_count += 1

                    db.session.commit()

                else:
                    global_errors = global_errors + errors
                    error_lines.append(line)

        if not global_errors and new_channels_count > 0:
            return PlugItRedirect('channels/?saved=yes&newchannelscount=' + str(new_channels_count))
        if new_channels_count == 0:
            global_errors.insert(0, "No new channel added.")
        else:
            global_errors.insert(0, str(new_channels_count) + " new channel were already added.")

    default_country = None

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
        if sp:
            cc_obj = Ecc.query.filter_by(iso=sp.location_country).first()
            default_country = cc_obj.id

    stations = []

    for station in Station.query.filter_by(
            orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))).all():
        stations.append(station.json)

    return {'importdata': data, 'errors': global_errors, 'error_lines': error_lines, 'stations': stations,
            'types_id': Channel.TYPE_ID_CHOICES,
            'default_country': default_country}


def string_to_channel(linedata, station):
    object = Channel()
    object.station_id = station

    # Split line
    data = linedata.split(',')

    if len(data) < 2:
        return None

    # Define Type
    object.name = data[0]
    object.type_id = data[1]

    # FM
    # name	fm	ecc	pid	frequency
    if object.type_id == 'fm':
        if len(data) < 5:
            return None
        # ECC
        cc_obj = Ecc.query.filter_by(iso=data[2].upper()).first()
        if not cc_obj:
            ecc_pi = data[2][:1].upper()
            ecc_ecc = data[2][1:].upper()
            cc_obj = Ecc.query.filter_by(pi=ecc_pi, ecc=ecc_ecc).first()
        if cc_obj:
            object.ecc_id = cc_obj.id
        # PI
        object.pi = data[3]
        object.frequency = data[4]

    # DAB
    # name	dab	ecc	eid	sid	scids	UAType	PA
    elif object.type_id == 'dab':
        if len(data) < 6:
            return None
        # ECC
        cc_obj = Ecc.query.filter_by(iso=data[2].upper()).first()
        if not cc_obj:
            ecc_pi = data[2][:1].upper()
            ecc_ecc = data[2][1:].upper()
            cc_obj = Ecc.query.filter_by(pi=ecc_pi, ecc=ecc_ecc).first()
        if cc_obj:
            object.ecc_id = cc_obj.id
        # eid
        object.eid = data[3]
        object.sid = data[4]
        object.scids = data[5]
        # Optional Elements
        if len(data) >= 7:
            object.appty_uatype = data[6]
        if len(data) >= 8:
            object.pa = data[7]

    # DRM
    # name	drm	sid
    elif object.type_id == 'drm':
        if len(data) < 3:
            return None
        # sid
        object.sid = data[2]

    # AMSS
    elif object.type_id == 'amss':
        if len(data) < 3:
            return None
        # sid
        object.sid = data[2]

    # HD Radio
    # name	hd	cc	tx
    elif object.type_id == 'hd':
        if len(data) < 4:
            return None
        # cc
        object.cc = data[2]
        object.tx = data[3]

    # IP
    # name	ip	fqdn	service id
    elif object.type_id == 'ip':
        if len(data) < 4:
            return None
        # cc
        object.fqdn = data[2]
        object.serviceIdentifier = data[3]

    else:
        return None

    return object


@action(route="/channels/delete/<id>")
@json_only()
@only_orga_admin_user()
def channels_delete(request, id):
    """Delete a channel."""

    object = Channel.query.join(Station).filter(Channel.id == int(id),
                                                Station.orga == int(request.args.get('ebuio_orgapk'))).first()

    db.session.delete(object)
    db.session.commit()

    if request.args.get('station_id'):
        return PlugItRedirect('stations/%s/channels?deleted=yes' % request.args.get('station_id'))
    return PlugItRedirect('channels/?deleted=yes')


@action(route="/channels/check/<id>")
@json_only()
@only_orga_member_user()
def channels_check(request, id):
    """Check (and return DNS info) about a channel."""

    object = Channel.query.join(Station).filter(Channel.id == int(id),
                                                Station.orga == int(request.args.get('ebuio_orgapk'))).first()

    (fqdn, vis, epg, tag) = object.dns_values

    return {'dns': object.radiodns_entry, 'fqdn': fqdn, 'expected_fqdn': object.station.fqdn,
            'radiovis': {'service': vis, 'exptected_service': object.station.radiovis_service},
            'radioepg': {'service': epg, 'exptected_service': object.station.radioepg_service},
            'radiotag': {'service': tag, 'exptected_service': object.station.radiotag_service}}


@action(route="/channels/export/", template="channels/export.html")
@only_orga_member_user()
def channels_export(request):
    """Export channels to zone file."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    retour = ''

    retour += '; GENERATED BY EBU RADIODNS MANAGER v2015\n'
    retour += '; http://ebu.io/rdns\n\n'
    retour += '; Service Provider  : ' + sp.medium_name + '\n'
    retour += '; EBU Codops        : ' + sp.codops + '\n'
    retour += '; Organization      : ' + orga.name + '\n'

    old_station_name = ''

    channel_elements = Channel.query.join(Station).filter(
        Station.orga == int(request.args.get('ebuio_orgapk'))).order_by(Station.name, Channel.name).all()
    dns_elements = [e.dns_entry for e in channel_elements]
    for elem in channel_elements:
        if elem.station_ascii_name != old_station_name:
            # If Channel Name changes output a new Station header
            retour += '\n;;; Station: ' + elem.station_ascii_name + '\n'
            old_station_name = elem.station_ascii_name

        # Ignore IP Channels in Zone File
        if elem.type_id != 'id':
            # Add Entries for all channels in ns and iso format
            wildcard_elem = '*' + elem.dns_entry[elem.dns_entry.find('.'):]
            wildcards = Channel.query.join(Station).filter(Channel.dns_entry == wildcard_elem).all()
            if wildcard_elem not in dns_elements or elem.dns_entry == wildcard_elem:
                retour += elem.dns_entry.ljust(40) + '\tIN\tCNAME\t' + elem.station.fqdn + '\n'
                if elem.ecc_id:  # Output ISO version if element has ECC
                    retour += elem.dns_entry_iso.ljust(40) + '\tIN\tCNAME\t' + elem.station.fqdn + '\n'

    if request.args.get('to') == 'file':
        retour_str = StringIO.StringIO()
        retour_str.write(str(retour))
        retour_str.seek(0)
        return PlugItSendFile(retour_str, 'text/plain', True, sp.codops.lower() + '-radio-ebu-io-zone')

    return {'retour': retour}
