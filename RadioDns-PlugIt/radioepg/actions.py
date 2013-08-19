# -*- coding: utf-8 -*-

# Utils
from utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only, PlugItSendFile, addressInNetwork

from models import db, Station, Channel, Show, Ecc, LogEntry, Schedule

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

    if len(stations_json) == 0:
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

    if len(stations_json) == 0:
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
    """Move an event"""

    station = Station.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    schedule = Schedule.query.filter_by(station_id=station.id, id=int(request.args.get('progPk'))).first()

    db.session.delete(schedule)
    db.session.commit()

    return {}


#[{"id":"2","title":"Nuit","start":1376938800,"end":1376971200,"allDay":false,"color":"#DDD","textColor":"#000"},{"id":"3","title":"Nuit","start":1377025200,"end":1377057600,"allDay":false,"color":"#DDD","textColor":"#000"},{"id":"4","title":"Nuit","start":1377111600,"end":1377144000,"allDay":false,"color":"#DDD","textColor":"#000"},{"id":"5","title":"Nuit","start":1377198000,"end":1377230400,"allDay":false,"color":"#DDD","textColor":"#000"},{"id":"6","title":"Morning Show","start":1376971200,"end":1376985600,"allDay":false,"color":"#F80","textColor":"#000"},{"id":"7","title":"NEWS","start":1376906400,"end":1376910000,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"8","title":"NEWS","start":1376992800,"end":1376996400,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"9","title":"NEWS","start":1377079200,"end":1377082800,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"10","title":"NEWS","start":1377165600,"end":1377169200,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"11","title":"NEWS","start":1377252000,"end":1377255600,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"12","title":"NEWS","start":1376935200,"end":1376938800,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"13","title":"NEWS","start":1377021600,"end":1377025200,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"14","title":"NEWS","start":1377108000,"end":1377111600,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"15","title":"NEWS","start":1377194400,"end":1377198000,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"16","title":"NEWS","start":1377280800,"end":1377284400,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"17","title":"Top DanceFloor","start":1377284400,"end":1377313200,"allDay":false,"color":"#FF8","textColor":"#000"},{"id":"18","title":"Top DanceFloor","start":1377370800,"end":1377399600,"allDay":false,"color":"#FF8","textColor":"#000"},{"id":"19","title":"Nuit","start":1377457200,"end":1377468000,"allDay":false,"color":"#DDD","textColor":"#000"},{"id":"20","title":"Nuit","start":1376863200,"end":1376884800,"allDay":false,"color":"#DDD","textColor":"#000"},{"id":"21","title":"Morning Show","start":1376884800,"end":1376899200,"allDay":false,"color":"#F80","textColor":"#000"},{"id":"22","title":"Morning Show","start":1377057600,"end":1377072000,"allDay":false,"color":"#F80","textColor":"#000"},{"id":"23","title":"Morning Show","start":1377144000,"end":1377158400,"allDay":false,"color":"#F80","textColor":"#000"},{"id":"24","title":"Morning Show","start":1377230400,"end":1377244800,"allDay":false,"color":"#F80","textColor":"#000"},{"id":"25","title":"Music Programme","start":1376899200,"end":1376906400,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"26","title":"Music Programme","start":1376985600,"end":1376992800,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"27","title":"Music Programme","start":1377072000,"end":1377079200,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"28","title":"Music Programme","start":1377158400,"end":1377165600,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"29","title":"Music Programme","start":1377244800,"end":1377252000,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"30","title":"Summer Afternoon","start":1376910000,"end":1376924400,"allDay":false,"color":"#FF0","textColor":"#000"},{"id":"31","title":"Summer Afternoon","start":1376996400,"end":1377010800,"allDay":false,"color":"#FF0","textColor":"#000"},{"id":"32","title":"Summer Afternoon","start":1377082800,"end":1377097200,"allDay":false,"color":"#FF0","textColor":"#000"},{"id":"33","title":"Summer Afternoon","start":1377169200,"end":1377183600,"allDay":false,"color":"#FF0","textColor":"#000"},{"id":"34","title":"Summer Afternoon","start":1377255600,"end":1377270000,"allDay":false,"color":"#FF0","textColor":"#000"},{"id":"35","title":"Summer Afternoon","start":1377342000,"end":1377363600,"allDay":false,"color":"#FF0","textColor":"#000"},{"id":"36","title":"AfterWork","start":1376924400,"end":1376935200,"allDay":false,"color":"#08F","textColor":"#000"},{"id":"37","title":"AfterWork","start":1377010800,"end":1377021600,"allDay":false,"color":"#08F","textColor":"#000"},{"id":"38","title":"AfterWork","start":1377097200,"end":1377108000,"allDay":false,"color":"#08F","textColor":"#000"},{"id":"39","title":"AfterWork","start":1377183600,"end":1377194400,"allDay":false,"color":"#08F","textColor":"#000"},{"id":"40","title":"AfterWork","start":1377270000,"end":1377280800,"allDay":false,"color":"#08F","textColor":"#000"},{"id":"41","title":"Rock session","start":1377363600,"end":1377370800,"allDay":false,"color":"#800","textColor":"#FFF"},{"id":"42","title":"Rock session","start":1377442800,"end":1377457200,"allDay":false,"color":"#800","textColor":"#FFF"},{"id":"43","title":"Live Session","start":1377428400,"end":1377442800,"allDay":false,"color":"#F0F","textColor":"#000"},{"id":"44","title":"NEWS","start":1377338400,"end":1377342000,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"45","title":"NEWS","start":1377424800,"end":1377428400,"allDay":false,"color":"#F00","textColor":"#FFF"},{"id":"46","title":"Music Programme","start":1377331200,"end":1377338400,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"47","title":"Music Programme","start":1377417600,"end":1377424800,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"48","title":"Music Programme","start":1377313200,"end":1377320400,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"49","title":"Music Programme","start":1377399600,"end":1377406800,"allDay":false,"color":"#0FF","textColor":"#000"},{"id":"50","title":"Morning Show","start":1377320400,"end":1377331200,"allDay":false,"color":"#F80","textColor":"#000"},{"id":"51","title":"Morning Show","start":1377406800,"end":1377417600,"allDay":false,"color":"#F80","textColor":"#000"}]