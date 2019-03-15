# -*- coding: utf-8 -*-
import plugit
from flask import jsonify
from plugit.api import PlugItAPI
# Utils
from plugit.utils import action, only_orga_admin_user, json_only, only_orga_member_user

import config
from SPI.event_listener.ORM_events_listeners import spi_generator_manager
from actions_utils import get_orga_service_provider
from aws import awsutils


@action(route="/system/", template="system/home.html")
@only_orga_admin_user()
def system_home(request):
    """Show the system status."""

    plugitapi = PlugItAPI(config.API_URL)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    passworded = request.args.get('passworded') == 'yes'

    return {'saved': saved, 'deleted': deleted}


@action(route="/system/check")
@json_only()
@only_orga_admin_user()
def system_check(request):
    """Check AWS State for Service Provider."""

    return awsutils.check_mainzone()


@plugit.app.route('/')
@json_only()
def system_info():
    return jsonify({'app': 'RadioDNS SPI/EPG server', 'revision': config.REVISION})


@action(route="/spi_generate", methods=['GET'])
@json_only()
@only_orga_member_user()
def spi_generate(request):
    try:
        _, sp = get_orga_service_provider(request)
        spi_generator_manager.tell_to_actor({"type": "add", "subject": "reload", "id": sp.id, "action": "update"})
    except Exception as e:
        print(e)
    finally:
        return {"ok": "ok"}


@action(route="/spi_generate_all", methods=['GET'])
@json_only()
@only_orga_admin_user()
def spi_generate_all(request):
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "all", "action": "update"})
    return {"ok": "ok"}
