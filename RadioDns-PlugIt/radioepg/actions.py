# -*- coding: utf-8 -*-

# Utils
from utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile, addressInNetwork

from models import db, Station, Channel, Show, Ecc, LogEntry

import urlparse

import os
import sys
import time

from werkzeug import secure_filename
from flask import abort

from PIL import Image
import imghdr

import config

@action(route="/radioepg/shows/", template="radioepg/shows/home.html")
@only_orga_member_user()
def radioepg_shows_home(request):
    """Show the list of shows."""

    list = []

    for elem in Show.query.filter_by(orga = int(request.args.get('ebuio_orgapk'))).order_by(Show.medium_name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    
    return {'list': list, 'saved': saved, 'deleted': deleted}


@action(route="/radioepg/shows/edit/<id>", template="radioepg/shows/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def radioepg_shows_edit(request, id):
    """Edit a show."""

    object = None
    errors = []

    if id != '-':
        object =  Show.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = Show(int(request.form.get('ebuio_orgapk')))

        object.medium_name = request.form.get('medium_name')
        object.long_name = request.form.get('long_name')
        object.description = request.form.get('description')
        object.color = request.form.get('color')


        # Check errors
        if object.medium_name == '':
            errors.append("Please set a medium name")

        if object.long_name == '':
            errors.append("Please set a long name")

        if object.description == '':
            errors.append("Please set a description")

        if object.color == '':
            errors.append("Please set a color")

        # If no errors, save
        if not errors:
            
            if not object.id:
                db.session.add(object)

            db.session.commit()

            return PlugItRedirect('radioepg/shows/?saved=yes')

    if object:
        object = object.json

    colors = [('Red', '#e41a1c'), ('Blue', '#377eb8'), ('Green', '#4daf4a'), ('Magenta', '#984ea3'), ('Orange', '#ff7f00'), ('Yellow', '#ffff33'), ('Brown', '#a65628'), ('Pink', '#f781bf'), ('Gray', '#999999')]
       
    return {'object': object, 'colors': colors,  'errors': errors}

@action(route="/radioepg/shows/delete/<id>")
@json_only()
@only_orga_admin_user()
def radioepg_shows_delete(request, id):
    """Delete a show."""

    object = Show.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    
    os.unlink(object.filename)
    
    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('radioepg/shows/?deleted=yes')