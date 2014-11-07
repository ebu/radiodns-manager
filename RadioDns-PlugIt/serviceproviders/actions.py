# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only

from models import db, ServiceProvider
from plugit.api import PlugItAPI, Orga
import config

import json


@action(route="/serviceproviders/", template="serviceproviders/home.html")
@only_orga_member_user()
def serviceproviders_home(request):
    """Show the list of serviceproviders."""

    list = []

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    passworded = request.args.get('passworded') == 'yes'

    return {'serviceprovider': sp, 'saved': saved, 'deleted': deleted}


@action(route="/serviceproviders/edit/<id>", template="serviceproviders/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def serviceproviders_edit(request, id):
    """Edit a serviceproviders."""

    object = None
    errors = []

    if id != '-':
        object = ServiceProvider.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = ServiceProvider(int(request.form.get('ebuio_orgapk')))

        object.name = request.form.get('name')
        object.short_name = request.form.get('short_name')
        object.short_description = request.form.get('short_description')
        object.ip_allowed = request.form.get('ip_allowed')

        genres = []

        genre_href = request.form.getlist('genrehref[]')
        genre_name = request.form.getlist('genrename[]')

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

            return PlugItRedirect('serviceproviders/?saved=yes')

    if object:
        object = object.json

    return {'object': object, 'errors': errors}


@action(route="/serviceproviders/delete/<id>")
@json_only()
@only_orga_admin_user()
def serviceproviders_delete(request, id):
    """Delete a ServiceProvider."""

    object = ServiceProvider.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('serviceproviders/?deleted=yes')


@action(route="/serviceproviders/newpassword/<id>")
@json_only()
@only_orga_admin_user()
def serviceproviders_newpassword(request, id):
    """Delete a ServiceProvider."""

    object = ServiceProvider.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    object.gen_random_password()
    db.session.commit()

    return PlugItRedirect('serviceproviders/?passworded=yes')
