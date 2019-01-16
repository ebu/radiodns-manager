# -*- coding: utf-8 -*-

from plugit.api import PlugItAPI
# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only

import config
from actions_utils import get_orga_service_provider
from aws import awsutils
from models import db, Station, ServiceProvider, LogoImage, Channel, GenericServiceFollowingEntry, Picture
from stations.utils import save_or_update_station, get_client_and_station, update_station_srv, \
    combine_client_and_station


@action(route="/stations/", template="stations/home.html")
@only_orga_member_user()
def stations_home(request):
    """Show the list of stations."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    stations = map(
        lambda station: station.json,
        Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), parent=None).order_by(Station.name).all(),
    )

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    passworded = request.args.get('passworded') == 'yes'

    if sp:
        sp = sp.json

    return {'serviceprovider': sp, 'ebu_codops': orga.codops,
            'stations': stations, 'saved': saved, 'deleted': deleted, 'passworded': passworded,
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

    clients, stations = get_client_and_station(request, id)

    if stations == [None]:
        return PlugItRedirect('')

    if sp:
        sp = sp.json

    pictures = []

    for elem in LogoImage.query.filter_by(orga=int(request.args.get('ebuio_orgapk'))).order_by(LogoImage.name).all():
        pictures.append(elem.json)

    return {'clients_stations': combine_client_and_station(request, clients, stations, False),
            'pictures': pictures, 'serviceprovider': sp, 'ebu_codops': orga.codops,
            'saved': saved, 'deleted': deleted}


@action(route="/stations/<id>/channels", template="stations/channels.html")
@only_orga_member_user()
def station_channels(request, id):
    """Show the list of channels."""

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

    orga_id = int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))
    orga, sp = get_orga_service_provider(request)
    errors = []
    clients, stations = get_client_and_station(request, id)

    if request.method == 'POST':
        station, errors = save_or_update_station(sp, request, errors, stations[0])
        update_station_srv(station)

        for client in clients[1:]:
            station_override = Station.query.filter_by(fk_client=client.id, parent=station.id, orga=orga_id).first()
            _, errors = save_or_update_station(sp, request, errors, station_override, client, station)
        db.session.commit()

        return PlugItRedirect('stations/' + str(station.id) + '?saved=yes')

    default_radiovis = ""
    default_radioepg = ""
    default_radiotag = ""
    default_radiospi = ""

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()
        if sp:
            default_radiovis = sp.vis_service
            default_radioepg = sp.epg_service
            default_radiotag = sp.tag_service
            default_radiospi = sp.spi_service

    if sp:
        sp = sp.json

    return {'clients_stations': combine_client_and_station(request, clients, stations),
            'errors': errors,
            'sp': sp,
            'id': id,
            'clients': map(lambda c: c.json, clients),
            'default_radiovis_service': default_radiovis,
            'default_radioepg_service': default_radioepg,
            'default_radiotag_service': default_radiotag,
            'default_radiospi_service': default_radiospi,
            'RADIOTAG_ENABLED': config.RADIOTAG_ENABLED,

            }


@action(route="/stations/delete/<id>")
@json_only()
@only_orga_admin_user()
def stations_delete(request, id):
    """Delete a station."""

    object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    if not config.STANDALONE:
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
            object.service_provider = sp

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
