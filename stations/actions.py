# -*- coding: utf-8 -*-

# Utils
from utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only

from models import db, Station


@action(route="/stations/", template="stations/home.html")
@only_orga_member_user()
def stations_home(request):
    """Show the list of stations."""

    list = []

    for elem in Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk'))).order_by(Station.name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    
    return {'list': list, 'saved': saved, 'deleted': deleted}


@action(route="/stations/edit/<id>", template="stations/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def stations_edit(request, id):
    """Edit a station."""

    object = None
    errors = []

    if id != '-':
        object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if request.method == 'POST':

        # Check errors
        if request.form.get('name', '') == '':
            errors.append("Please set a name")

        # If no errors, save
        if not errors:
            if not object:
                object = Station(int(request.form.get('ebuio_orgapk')))
            
            object.name = request.form.get('name')

            if not object.id:
                db.session.add(object)

            db.session.commit()

            return PlugItRedirect('stations/?saved=yes')

    else:
        if object:
            object = object.json
       
    return {'object': object, 'errors': errors}

@action(route="/stations/delete/<id>")
@json_only()
@only_orga_admin_user()
def stations_delete(request, id):
    """Delete a station."""

    object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('stations/?deleted=yes')
