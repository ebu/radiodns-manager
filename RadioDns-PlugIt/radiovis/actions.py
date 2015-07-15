# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile, addressInNetwork, no_template

from models import db, Station, Channel, Picture, Ecc, LogEntry, ServiceProvider
from plugit.api import PlugItAPI, Orga
import urlparse
from aws import awsutils

import os
import sys
import time
import uuid

from werkzeug import secure_filename
from flask import abort

from PIL import Image
import imghdr

import config


@action(route="/radiovis/gallery/", template="radiovis/gallery/home.html")
@only_orga_member_user()
def radiovis_gallery_home(request):
    """Show the list of pictures."""

    list = []

    for elem in Picture.query.filter_by(orga = int(request.args.get('ebuio_orgapk'))).order_by(Picture.name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'

    return {'list': list, 'saved': saved, 'deleted': deleted}


@action(route="/radiovis/gallery/edit/<id>", template="radiovis/gallery/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def radiovis_gallery_edit(request, id):
    """Edit a channel."""

    object = None
    errors = []

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()


    if id != '-':
        object = Picture.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = Picture(int(request.form.get('ebuio_orgapk')))

        if sp:
            object.image_url_prefix = sp.image_url_prefix

        object.name = request.form.get('name')
        object.radiotext = request.form.get('radiotext')
        object.radiolink = request.form.get('radiolink')

        def add_unique_postfix(fn):
            """__source__ = 'http://code.activestate.com/recipes/577200-make-unique-file-name/'"""
            if not os.path.exists(fn):
                return fn

            path, name = os.path.split(fn)
            name, ext = os.path.splitext(name)

            make_fn = lambda i: os.path.join(path, '%s(%d)%s' % (name, i, ext))

            for i in xrange(2, sys.maxint):
                uni_fn = make_fn(i)
                if not os.path.exists(uni_fn):
                    return uni_fn

            return None

        def unique_filename(fn):

            path, name = os.path.split(fn)
            name, ext = os.path.splitext(name)

            make_fn = lambda i: os.path.join(path, '%s%s' % (str(uuid.uuid4()), ext))

            for i in xrange(2, sys.maxint):
                uni_fn = make_fn(i)
                if not os.path.exists(uni_fn):
                    return uni_fn

            return None

        new_file = False
        if request.files:
            new_file = True
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                full_path = unique_filename('media/uploads/radiovis/gallery/' + filename)
                path, name = os.path.split(full_path)
                file.save(full_path)
                if object.filename:
                    try:
                        os.unlink(object.filename)
                    except:
                        pass
                object.filename = name

            # Check errors
            if object.name == '':
                errors.append("Please set a name")

            if object.radiotext == '':
                errors.append("Please set a text")

            if object.radiolink == '':
                errors.append("Please set a link")

            if object.filename == '' or object.filename is None:
                errors.append("Please upload an image")
            else:

                if imghdr.what(full_path) not in ['jpeg', 'png']:
                    errors.append("Image is not an png or jpeg image")
                    os.unlink(full_path)
                    object.filename = None
                else:
                    im = Image.open(full_path)
                    if im.size != (320, 240):
                        errors.append("Image must be 320x240")
                        del im
                        os.unlink(full_path)
                        object.filename = None

        pieces = urlparse.urlparse(object.radiolink)

        if pieces.scheme not in ['http', 'https', 'ftp']:
            errors.append("The link is not valid")

        # If no errors, save
        if not errors:

            # Upload to s3
            if new_file:
                try:
                    awsutils.upload_public_image(sp, name, full_path)
                except:
                    pass
            # TODO Clean up old images on S3

            if not object.id:
                db.session.add(object)

            db.session.commit()

            try:
                # Remove local copy
                os.unlink(full_path)
            except:
                pass

            return PlugItRedirect('radiovis/gallery/?saved=yes')

        try:
            # Remove local copy
            os.unlink(full_path)
        except:
            pass

    if object:
        object = object.json

    return {'object': object, 'errors': errors}


@action(route="/radiovis/gallery/delete/<id>")
@json_only()
@only_orga_admin_user()
def radiovis_gallery_delete(request, id):
    """Delete a picture."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    object = Picture.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()

    # Remove File
    try:
        os.unlink(object.filename)
    except:
        pass
    # Remove from S3
    try:
        awsutils.delete_public_image(sp, object.filename)
    except:
        pass

    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('radiovis/gallery/?deleted=yes')


@action(route="/radiovis/channels/", template="radiovis/channels/home.html")
@only_orga_member_user()
def radiovis_channels_home(request):
    """Show the list of channels to edit current picture."""

    list = []

    for elem in Channel.query.filter(Channel.type_id!='id').join(Station).filter(Station.orga==int(request.args.get('ebuio_orgapk'))).order_by(Station.name,Channel.type_id,Channel.name).all():
        list.append(elem.json)

    pictures = []

    for elem in Picture.query.filter_by(orga = int(request.args.get('ebuio_orgapk'))).order_by(Picture.name).all():
        pictures.append(elem.json)

    return {'list': list, 'pictures': pictures}

@action(route="/radiovis/channels/player/", template="radiovis/channels/player.html")
@no_template()
def radiovis_channels_player(request):
    """Show a simple Player."""

    topic = request.args.get('topic')
    stationname = request.args.get('stationname')
    name = request.args.get('name')

    return {'stationname': stationname, 'name': name, 'topic': topic}

@action(route="/radiovis/channels/playermodal/", template="radiovis/channels/playermodal.html")
@no_template()
def radiovis_channels_playermodal(request):
    """Show a simple Player."""

    topic = request.args.get('topic')
    stationname = request.args.get('stationname')
    name = request.args.get('name')

    return {'stationname': stationname, 'name': name, 'topic': topic}


@action(route="/radiovis/channels/set/<id>/<pictureid>")
@only_orga_admin_user()
@json_only()
def radiovis_channels_set(request, id, pictureid):
    """Set a default value for a channel"""

    object = Channel.query.join(Station).filter(Channel.id == int(id), Station.orga==int(request.args.get('ebuio_orgapk'))).first()

    picture = Picture.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(pictureid)).first()

    if picture:
        object.default_picture_id = picture.id
    else:
        object.default_picture_id = None

    db.session.commit()

    return {}


@action(route="/radiovis/channels/logs/<id>/", template="radiovis/channels/logs.html")
@only_orga_admin_user()
def radiovis_channels_logs(request, id):
    """Show logs for a channel"""

    object = Channel.query.join(Station).filter(Channel.id == int(id), Station.orga==int(request.args.get('ebuio_orgapk'))).first()

    if not object:
        abort(404)
        return

    list = []

    for logentry in LogEntry.query.filter(LogEntry.topic.ilike(object.topic + '%')).order_by(-LogEntry.reception_timestamp).all():
        list.append(logentry.json)

    return {'list': list, 'channel': object.json}


@action(route="/radiovis/api/<secret>/check_auth")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_check_auth(request, secret):
    """Api call to authenticate a station"""

    if secret != config.API_SECRET:
        abort(404)
        return

    user = request.form.get('username')
    password = request.form.get('password')
    ip = request.form.get('ip')

    # Find the station
    id = user.split('.')[0]

    object = Station.query.filter_by(id=int(id)).first()

    if not object:
        return {'result': False, 'error': 'No station'}

    if object.stomp_username != user:
        return {'result': False, 'error': 'Wrong username'}

    if object.random_password != password:
        return {'result': False, 'error': 'Wrong password'}

    if ip:
        allowd = False

        for subnetAllowed in object.ip_allowed.split(','):
            if addressInNetwork(ip, subnetAllowed):
                allowd = True
                break

        if not allowd:
            return {'result': False, 'error': 'IP not allowed'}

    return {'result': True}


@action(route="/radiovis/api/<secret>/get_channels")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_get_channels(request, secret):
    """Api call to get a list of channels"""

    if secret != config.API_SECRET:
        abort(404)
        return

    list = []

    object = Station.query.filter_by(id=int(request.form.get('station_id'))).first()

    for channel in object.channels:
        list.append(channel.topic)

    return {'list': list}


@action(route="/radiovis/api/<secret>/get_gcc")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_get_gcc(request, secret):
    """Api call to get a gcc based on a cc"""

    if secret != config.API_SECRET:
        abort(404)
        return

    object = Ecc.query.filter_by(iso=request.form.get('cc').upper()).first()

    return {'gcc': (object.pi + object.ecc).lower()}


@action(route="/radiovis/api/<secret>/get_all_channels")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_get_all_channels(request, secret):
    """Retrun the list of all channels"""

    if secret != config.API_SECRET:
        abort(404)
        return

    list = []

    for channel in Channel.query.all():
        list.append((channel.topic, channel.id))

    return {'list': list}

@action(route="/radiovis/api/<secret>/get_all_vis_channels")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_get_all_vis_channels(request, secret):
    """Retrun the list of all channels"""

    if secret != config.API_SECRET:
        abort(404)
        return

    list = []

    for channel in Channel.query.filter(Channel.default_picture_id != None).all():
        list.append((channel.topic, channel.id))

    return {'list': list}

@action(route="/radiovis/api/<secret>/get_channel_default")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_get_channel_default(request, secret):
    """Return the default value for a channel"""

    if secret != config.API_SECRET:
        abort(404)
        return

    channel = Channel.query.filter_by(id=request.form.get('id')).first()

    if channel and channel.default_picture:
        return {'info': channel.default_picture.json}
    else:
        return {'info': None}


@action(route="/radiovis/api/<secret>/cleanup_logs")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_cleanup_logs(request, secret):
    """Cleanup logs if timestamp < time.time() - max_age"""

    if secret != config.API_SECRET:
        abort(404)
        return

    # The following was not optimal thus replaced by RAW SQL
    # for object in LogEntry.query.filter(LogEntry.reception_timestamp < (time.time() - int(request.form.get('max_age')))).all():
    #     db.session.delete(object)
    #
    # db.session.commit()
    from sqlalchemy.sql import text
    db.engine.execute(text('DELETE FROM log_entry WHERE reception_timestamp <  :t'),
                      t = (time.time() - int(request.form.get('max_age'))))

    return {}


@action(route="/radiovis/api/<secret>/add_log")
@only_orga_admin_user()  # To prevent call from IO
@json_only()
def radiovis_api_add_log(request, secret):
    """Add a new log entrie"""

    if secret != config.API_SECRET:
        abort(404)
        return

    object = LogEntry()

    object.topic = request.form.get('topic')
    object.body = request.form.get('message')
    object.headers = request.form.get('headers')
    object.reception_timestamp = int(request.form.get('timestamp'))

    db.session.add(object)

    db.session.commit()

    return {}
