# -*- coding: utf-8 -*-
import plugit
from plugit.api import PlugItAPI
# Utils
from plugit.utils import action, only_orga_admin_user, json_only

import config
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
    return {'app': 'RadioDNS SPI/EPG server', 'revision': config.REVISION}
