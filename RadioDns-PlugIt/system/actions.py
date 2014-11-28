# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only

from models import db, ServiceProvider, LogoImage
from plugit.api import PlugItAPI, Orga
import config

import os
import sys
import time

from werkzeug import secure_filename
from PIL import Image
import imghdr


import json
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

