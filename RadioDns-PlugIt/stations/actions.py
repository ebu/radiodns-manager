# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only
from plugit.api import PlugItAPI, Orga
import config
from models import db, Station, ServiceProvider, LogoImage, Channel, GenericServiceFollowingEntry, Picture
from aws import awsutils
import json


@action(route="/stations/", template="stations/home.html")
@only_orga_member_user()
def stations_home(request):
    """Show the list of stations."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    list = []

    for elem in Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk'))).order_by(Station.name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    passworded = request.args.get('passworded') == 'yes'

    if sp:
        sp = sp.json

    return {'serviceprovider': sp, 'ebu_codops': orga.codops,
            'list': list, 'saved': saved, 'deleted': deleted, 'passworded': passworded,
            'RADIOTAG_ENABLED': config.RADIOTAG_ENABLED}


@action(route="/stations/<id>", template="stations/details.html")
@only_orga_member_user()
def station_details(request, id):
    """Show the station."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'

    station = None
    if id != '-':
        station = Station.query.filter_by(
            orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if not station:
        return PlugItRedirect('')

    if sp:
        sp = sp.json

    pictures = []

    for elem in LogoImage.query.filter_by(orga=int(request.args.get('ebuio_orgapk'))).order_by(LogoImage.name).all():
        pictures.append(elem.json)

    return {'station': station.json, 'pictures': pictures, 'serviceprovider': sp, 'ebu_codops': orga.codops,
            'saved': saved, 'deleted': deleted}


@action(route="/stations/<id>/channels", template="stations/channels.html")
@only_orga_member_user()
def station_channels(request, id):
    """Show the list of channels."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    saved = request.args.get('saved') == 'yes'
    newchannelscount = request.args.get('newchannelscount')
    deleted = request.args.get('deleted') == 'yes'

    station = None
    if id != '-':
        station = Station.query.filter_by(id=int(id),
                                          orga=int(request.args.get('ebuio_orgapk') or request.form.get(
                                              'ebuio_orgapk'))).first()

    if not station:
        return PlugItRedirect('')

    expected_fqdn = station.service_provider.fqdn

    list = []

    for elem in Channel.query.join(Station).filter(Station.id == int(id)).order_by(
            Station.name, Channel.type_id, Channel.name).all():
        list.append(elem.json)

    return {'list': list, 'station': station.json, 'expected_fqdn': expected_fqdn,
            'saved': saved, 'deleted': deleted, 'newchannelscount': newchannelscount}


@action(route="/stations/<id>/radiovis/channels", template="stations/radiovis.html")
@only_orga_member_user()
def station_radiovis_channels(request, id):
    """Show the list of channels to edit current picture."""

    station = None
    if id != '-':
        station = Station.query.filter_by(id=int(id),
                                          orga=int(request.args.get('ebuio_orgapk') or request.form.get(
                                              'ebuio_orgapk'))).first()

    if not station:
        return PlugItRedirect('')

    list = []

    for elem in Channel.query.filter(Channel.type_id != 'id').join(Station).filter(
            Station.id == station.id and Station.orga == int(
                request.args.get('ebuio_orgapk'))).order_by(Channel.type_id, Channel.name).all():
        list.append(elem.json)

    pictures = []

    for elem in Picture.query.filter_by(orga=int(request.args.get('ebuio_orgapk'))).order_by(Picture.name).all():
        pictures.append(elem.json)

    return {'list': list, 'pictures': pictures, 'station': station.json}


@action(route="/stations/<id>/radioepg/servicefollowing", template="stations/servicefollowing.html")
@only_orga_member_user()
def station_epg_sf(request, id):
    """Show the list to manage service following."""

    station = None
    if id != '-':
        station = Station.query.filter_by(id=int(id),
                                          orga=int(request.args.get('ebuio_orgapk') or request.form.get(
                                              'ebuio_orgapk'))).first()

    if not station:
        return PlugItRedirect('')

    # Build list of entries
    list = []

    # Channels
    for elem in station.channels.order_by(Channel.name).all():
        list.append(elem.servicefollowingentry.json)

    # Custom entries
    for elem in station.servicefollowingentries.order_by(GenericServiceFollowingEntry.channel_uri).all():
        list.append(elem.json)

    return {'list': list, 'current_station_id': station.id, 'station': station.json}


@action(route="/stations/edit/<id>", template="stations/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def stations_edit(request, id):
    """Edit a station."""

    object = None
    errors = []

    if id != '-':
        object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')),
                                         id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = Station(int(request.form.get('ebuio_orgapk')))
            plugitapi = PlugItAPI(config.API_URL)
            orga = plugitapi.get_orga(request.form.get('ebuio_orgapk'))

            if orga.codops:
                sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
                if sp:
                    object.service_provider = sp

        object.name = request.form.get('name')
        object.short_name = request.form.get('short_name')
        object.medium_name = request.form.get('medium_name')
        object.long_name = request.form.get('long_name')
        object.short_description = request.form.get('short_description')
        object.long_description = request.form.get('long_description')
        object.url_default = request.form.get('url_default')
        object.ip_allowed = request.form.get('ip_allowed')

        object.postal_name = request.form.get('postal_name')
        object.street = request.form.get('street')
        object.city = request.form.get('city')
        object.zipcode = request.form.get('zipcode')
        object.phone_number = request.form.get('phone_number')
        object.sms_number = request.form.get('sms_number')
        object.sms_body = request.form.get('sms_body')
        object.sms_description = request.form.get('sms_description')
        object.keywords = request.form.get('keywords')
        object.email_address = request.form.get('email_address')
        object.email_description = request.form.get('email_description')

        object.default_language = request.form.get('default_language')
        object.location_country = request.form.get('location_country')

        genres = []

        genre_href = request.form.getlist('genrehref[]')
        genre_href = filter(None, genre_href)
        genre_name = request.form.getlist('genrename[]')
        genre_name = filter(None, genre_name)

        # Services
        object.radiovis_service = request.form.get('radiovis_service')
        radiovis_enabled = False
        if 'radiovis_enabled' in request.form:
            radiovis_enabled = True
            awsutils.update_or_create_vissrv_station(object)
        else:
            if object.radiovis_enabled:
                # Previously enabled
                awsutils.remove_vissrv_station(object)
        object.radiovis_enabled = radiovis_enabled

        object.radioepg_service = request.form.get('radioepg_service')
        radioepg_enabled = False
        if 'radioepg_enabled' in request.form:
            radioepg_enabled = True
            awsutils.update_or_create_epgsrv_station(object)
        else:
            if object.radioepg_enabled:
                # Previously enabled
                awsutils.remove_epgsrv_station(object)
        object.radioepg_enabled = radioepg_enabled

        # RadioEPG Program Information Service
        radioepgpi_enabled = False
        if 'radioepgpi_enabled' in request.form:
            radioepgpi_enabled = True
        object.radioepgpi_enabled = radioepgpi_enabled

        object.radiotag_service = request.form.get('radiotag_service')
        radiotag_enabled = False
        if 'radiotag_enabled' in request.form:
            radiotag_enabled = True
            awsutils.update_or_create_tagsrv_station(object)
        else:
            if object.radiotag_enabled:
                # Previously enabled
                awsutils.remove_tagsrv_station(object)
        object.radiotag_enabled = radiotag_enabled

        for h in genre_href:
            genres.append({'href': h, 'name': genre_name.pop(0)})

        object.genres = json.dumps(genres)

        # Check errors
        if object.name == '':
            errors.append("Please set a name")

        # If no errors, save
        if not errors:

            if not object.id:
                object.gen_random_password()
                db.session.add(object)

            db.session.commit()

            return PlugItRedirect('stations/' + str(object.id) + '?saved=yes')

    default_radiovis = ""
    default_radioepg = ""
    default_radiotag = ""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
        if sp:
            default_radiovis = sp.vis_service
            default_radioepg = sp.epg_service
            default_radiotag = sp.tag_service

    if sp:
        sp = sp.json

    if object:
        object = object.json

    return {'object': object, 'errors': errors,
            'sp': sp,
            'default_radiovis_service': default_radiovis,
            'default_radioepg_service': default_radioepg,
            'default_radiotag_service': default_radiotag,
            'RADIOTAG_ENABLED': config.RADIOTAG_ENABLED}


@action(route="/stations/delete/<id>")
@json_only()
@only_orga_admin_user()
def stations_delete(request, id):
    """Delete a station."""

    object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    awsutils.remove_station(object)
    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('stations/?deleted=yes')


@action(route="/stations/newpassword/<id>")
@json_only()
@only_orga_admin_user()
def stations_newpassword(request, id):
    """Delete a station."""

    object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    object.gen_random_password()
    db.session.commit()

    return PlugItRedirect('stations/?passworded=yes')


@action(route="/stations/linkserviceprovider/<id>")
@json_only()
@only_orga_admin_user()
def stations_linkserviceprovider(request, id):
    """Link station to its service provider."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
        if sp:
            object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
            object.service_provider = sp;

            db.session.commit()

    return PlugItRedirect('stations/?serviceprovider=yes')


@action(route="/stations/check/<id>")
@json_only()
@only_orga_member_user()
def station_check(request, id):
    """Check AWS State for Station."""

    plugitapi = PlugItAPI(config.API_URL)

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()

    if station:
        return station.check_aws()

    return {'isvalid': False}
