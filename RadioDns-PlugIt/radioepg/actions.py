# -*- coding: utf-8 -*-

# Utils
from utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile, addressInNetwork

from models import db, Station, Channel, Show, Ecc, LogEntry, Schedule, GenericServiceFollowingEntry

import urlparse

import os
import sys
import time

from werkzeug import secure_filename
from flask import abort

from PIL import Image
import imghdr

import config

def stations_lists(orga):
    list = {}
    list_json = []

    for elem in Station.query.filter_by(orga=orga).order_by(Station.name).all():
        list_json.append(elem.json)
        list[elem.id] = elem

    return (list_json, list)

@action(route="/radioepg/shows/", template="radioepg/shows/home.html")
@only_orga_member_user()
def radioepg_shows_home(request):
    """Show the list of shows."""

    (stations_json, stations) = stations_lists(int(request.args.get('ebuio_orgapk')))

    if not stations_json:
        return {'nostations': True}

    current_station_id = int(request.args.get('station_id', stations_json[0]['id']))
    current_station = stations[current_station_id]
 
    list = []

    for elem in current_station.shows.order_by(Show.medium_name).all():
        list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    
    return {'list': list, 'saved': saved, 'deleted': deleted, 'current_station_id': current_station_id, 'current_station': current_station.json, 'stations': stations_json  }


@action(route="/radioepg/shows/edit/<id>", template="radioepg/shows/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def radioepg_shows_edit(request, id):
    """Edit a show."""

    station_id = request.args.get('station_id')

    object = None
    errors = []

    if id != '-':
        object =  Show.query.filter_by(orga=int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')), id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = Show(int(request.form.get('ebuio_orgapk')))
            object.station_id = station_id

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
       
    return {'object': object, 'colors': colors,  'errors': errors, 'current_station_id': station_id }

@action(route="/radioepg/shows/delete/<id>")
@json_only()
@only_orga_admin_user()
def radioepg_shows_delete(request, id):
    """Delete a show."""

    object = Show.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
       
    db.session.delete(object)
    db.session.commit()

    station_id = request.args.get('station_id')

    return PlugItRedirect('radioepg/shows/?deleted=yes&station_id=' + station_id)

@action(route="/radioepg/schedule/", template="radioepg/schedule/home.html")
@only_orga_member_user()
def radioepg_schedule_home(request):
    """Show the schedule."""

    (stations_json, stations) = stations_lists(int(request.args.get('ebuio_orgapk')))

    if not stations_json:
        return {'nostations': True}

    current_station_id = int(request.args.get('station_id', stations_json[0]['id']))
    current_station = stations[current_station_id]

    list = []

    for elem in current_station.shows.order_by(Show.medium_name).all():
        list.append(elem.json)

    return {'shows': list, 'current_station_id': current_station_id, 'current_station': current_station.json, 'stations': stations_json}


@action(route="/radioepg/schedule/<id>/events")
@json_only()
@only_orga_member_user()
def radioepg_schedule_get_events(request, id):
    """Show events of a station"""

    object = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()

    start_date = int(request.args.get('start'))

    list = []

    for sche in object.schedules.all():
        list.append(dict(id=sche.id, title=sche.show.medium_name, start=start_date+sche.seconds_from_base, end=start_date+sche.
            seconds_from_base+sche.length*60, allDay=False, color=sche.show.color, textColor='#000'))

    return {'list': list}


@action(route="/radioepg/schedule/<id>/create/")
@json_only()
@only_orga_admin_user()
def radioepg_schedule_add_events(request, id):
    """Add a new event in a station schdule"""

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    show = Show.query.filter_by(station_id=station.id, id=int(request.args.get('showPk'))).first()

    (hour, minutes) = request.args.get('start').split(':')

    sche = Schedule()
    sche.show_id = show.id
    sche.station_id = station.id
    sche.day = request.args.get('timeday')
    sche.start_hour = hour
    sche.start_minute = minutes
    sche.length = 60

    db.session.add(sche)
    db.session.commit()

    return {}

@action(route="/radioepg/schedule/<id>/resize/")
@json_only()
@only_orga_admin_user()
def radioepg_schedule_resize_events(request, id):
    """Resize an event"""

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    schedule = Schedule.query.filter_by(station_id=station.id, id=int(request.args.get('progPk'))).first()

    schedule.length += int(request.args.get('deltaMinutes'))
    db.session.commit()

    return {}

@action(route="/radioepg/schedule/<id>/move/")
@json_only()
@only_orga_admin_user()
def radioepg_schedule_move_events(request, id):
    """Move an event"""

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    schedule = Schedule.query.filter_by(station_id=station.id, id=int(request.args.get('progPk'))).first()

    (schedule.start_hour, schedule.start_minute) = request.args.get('newStart').split(':')
    schedule.day += int(request.args.get('deltaDay'))
    db.session.commit()

    return {}

@action(route="/radioepg/schedule/<id>/delete/")
@json_only()
@only_orga_admin_user()
def radioepg_schedule_delete_events(request, id):
    """Delete an event"""

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    schedule = Schedule.query.filter_by(station_id=station.id, id=int(request.args.get('progPk'))).first()

    db.session.delete(schedule)
    db.session.commit()

    return {}

@action(route="/radioepg/schedule/<id>/xml", template='radioepg/schedule/xml.html')
@only_orga_member_user()
def radioepg_schedule_xml(request, id):
    """Display Schedule as XML"""

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()

    import datetime, time

    time_format = '%Y%m%dT%H%M%S'

    today = datetime.date.today()
    start_date = datetime.datetime.combine(today - datetime.timedelta(days=today.weekday()), datetime.time())
    end_date = start_date + datetime.timedelta(days=6,hours=23,minutes=59,seconds=59)

    list = []

    for elem in station.schedules.all():
        elem.start_date = start_date
        list.append(elem.json)

    return {'schedules': list, 'start_time': start_date.strftime(time_format), 'end_time': end_date.strftime(time_format)}

@action(route="/radioepg/servicefollowing/", template="radioepg/servicefollowing/home.html")
@only_orga_member_user()
def radioepg_sf_home(request):
    """Show the list to manage service following."""

    (stations_json, stations) = stations_lists(int(request.args.get('ebuio_orgapk')))

    if not stations_json:
        return {'nostations': True}

    current_station_id = int(request.args.get('station_id', stations_json[0]['id']))
    current_station = stations[current_station_id]
 
    # Build list of entries
    list = []

    # Channels
    for elem in current_station.channels.order_by(Channel.name).all():
        list.append(elem.servicefollowingentry.json)

    # Custom entries
    for elem in current_station.servicefollowingentries.order_by(GenericServiceFollowingEntry.channel_uri).all():
        list.append(elem.json)
    
    return {'list': list, 'current_station_id': current_station_id, 'current_station': current_station.json, 'stations': stations_json  }


@action(route="/radioepg/servicefollowing/edit/<id>", template="radioepg/servicefollowing/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def radioepg_servicefollowing_edit(request, id):
    """Edit a servicefollowing entry."""

    station_id = request.args.get('station_id')

    if not station_id:
        return None

    object = None
    errors = []

    if id != '-':
        object =  GenericServiceFollowingEntry.query.filter_by(id=int(id)).first()

        # Check rights
        if object.type == 'ip':
            station_to_test = object.station
        else:
            station_to_test = object.channel.station

        if station_to_test.id != int(station_id) or not station_to_test.orga == int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')):
            object = None

    if request.method == 'POST':

        if not object:
            object = GenericServiceFollowingEntry()
            object.station_id = station_id

        object.cost = request.form.get('cost')
        object.offset = request.form.get('offset')
        object.mime_type = request.form.get('mime_type')

        if object.type == 'ip':
            object.channel_uri = request.form.get('channel_uri')

        # Check errors
        if object.type == 'ip' and object.channel_uri == '':
            errors.append("You have to set the channel")

        # If no errors, save
        if not errors:
            if not object.id:
                db.session.add(object)

            db.session.commit()

            return PlugItRedirect('radioepg/servicefollowing/?saved=yes')

    if object:
        object = object.json

    dab_mime_types = [('audio/mpeg', 'DAB'), ('audio/aacp', 'DAB+')]
      
    return {'object': object, 'dab_mime_types': dab_mime_types, 'errors': errors, 'current_station_id': station_id }


@action(route="/radioepg/servicefollowing/delete/<id>")
@json_only()
@only_orga_admin_user()
def radioepg_servicefollowing_delete(request, id):
    """Delete a servicefollowing entry."""

    object =  GenericServiceFollowingEntry.query.filter_by(id=int(id)).first()

    station_id = request.args.get('station_id')

    if not station_id:
        return None

    # Check rights before delete


       
    if object.type == 'ip':
        if object.station.id == int(station_id):
            if object.station.orga == int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')):
                db.session.delete(object)
                db.session.commit()

    

    return PlugItRedirect('radioepg/servicefollowing/?deleted=yes&station_id=' + station_id)

@action(route="/radioepg/servicefollowing/turn/<mode>/<id>")
@json_only()
@only_orga_admin_user()
def radioepg_servicefollowing_trun(request, mode, id):
    """Turn on or off a servicefollowing entry."""

    object =  GenericServiceFollowingEntry.query.filter_by(id=int(id)).first()

    station_id = request.args.get('station_id')

    if not station_id:
        return None

    if object.type == 'ip':
        station_to_test = object.station
    else:
        station_to_test = object.channel.station

    # Check rights before change
    if station_to_test.id == int(station_id):
        if station_to_test.orga == int(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk')):
            object.active = mode == 'on'
            db.session.commit()

    return PlugItRedirect('radioepg/servicefollowing/?turned=' + mode + '&station_id=' + station_id)

@action(route="/radioepg/servicefollowing/xml", template='radioepg/servicefollowing/xml.html')
@only_orga_member_user()
def radioepg_servicefollowing_xml(request):
    """Display servicefollowing as XML"""

    stations = Station.query.all()

    import datetime

    time_format = '%Y%m%dT%H%M%S'

    list = []

    for elem in stations:

        entries = []

        # Channels
        for elem2 in elem.channels.order_by(Channel.name).all():
            if elem2.servicefollowingentry.active:
                entries.append(elem2.servicefollowingentry.json)

        # Custom entries
        for elem2 in elem.servicefollowingentries.order_by(GenericServiceFollowingEntry.channel_uri).all():
            if elem2.active:
                entries.append(elem2.json)

        if entries:
            list.append([elem.json, entries])

    return {'stations': list, 'creation_time': datetime.datetime.now().strftime(time_format)}