# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only
from plugit.api import PlugItAPI, Orga
import config
from models import db, Station, ServiceProvider

import json


@action(route="/stations/", template="stations/home.html")
@only_orga_member_user()
def stations_home(request):
    """Show the list of stations."""

    list = []

    for elem in Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk'))).order_by(Station.name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    passworded = request.args.get('passworded') == 'yes'

    return {'list': list, 'saved': saved, 'deleted': deleted, 'passworded': passworded, 'RADIOTAG_ENABLED': config.RADIOTAG_ENABLED}


@action(route="/stations/edit/<id>", template="stations/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def stations_edit(request, id):
    """Edit a station."""

    object = None
    errors = []

    if id != '-':
        object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = Station(int(request.form.get('ebuio_orgapk')))

        object.name = request.form.get('name')
        object.short_name = request.form.get('short_name')
        object.short_description = request.form.get('short_description')
        object.ip_allowed = request.form.get('ip_allowed')

        genres = []

        genre_href = request.form.getlist('genrehref[]')
        genre_name = request.form.getlist('genrename[]')

        # Services
        radiovis_enabled = False
        if 'radiovis_enabled' in request.form:
            radiovis_enabled = True
        object.radiovis_enabled = radiovis_enabled
        object.radiovis_service = request.form.get('radiovis_service')
        radioepg_enabled = False
        if 'radioepg_enabled' in request.form:
            radioepg_enabled = True
        object.radioepg_enabled = radioepg_enabled
        object.radioepg_service = request.form.get('radioepg_service')
        radiotag_enabled = False
        if 'radiotag_enabled' in request.form:
            radiotag_enabled = True
        object.radiotag_enabled = radiotag_enabled
        object.radiotag_service = request.form.get('radiotag_service')

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

            return PlugItRedirect('stations/?saved=yes')

    if object:
        object = object.json

    return {'object': object, 'errors': errors,
            'default_radiovis_service':config.RADIOVIS_SERVICE_DEFAULT,
            'default_radioepg_service':config.RADIOEPG_SERVICE_DEFAULT,
            'default_radiotag_service':config.RADIOTAG_SERVICE_DEFAULT,
            'RADIOTAG_ENABLED': config.RADIOTAG_ENABLED}


@action(route="/stations/delete/<id>")
@json_only()
@only_orga_admin_user()
def stations_delete(request, id):
    """Delete a station."""

    object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
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
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()

    if station:
        return station.check_aws()

    return {'isvalid': False}