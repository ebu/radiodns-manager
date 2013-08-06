# -*- coding: utf-8 -*-

# Utils
from utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only

from models import db, Station, Channel


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
        object = Channel.query.join(Station).filter(Station.orga==int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))).filter_by(id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = Channel()


        object.name = request.form.get('name')
        object.station_id = int(request.form.get('station'))

        # Check errors
        if object.name == '':
            errors.append("Please set a name")

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
       
    return {'object': object, 'errors': errors, 'stations': stations}

@action(route="/channels/delete/<id>")
@json_only()
@only_orga_admin_user()
def channels_delete(request, id):
    """Delete a channel."""

    object = Channel.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('channels/?deleted=yes')
