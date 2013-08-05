# -*- coding: utf-8 -*-

# Include main methods
from main.actions import *

# Include stations methods
from stations.actions import *

from utils import action


@action(route="/menubar", template="menubar.html")
def menubar(request):
    """Dummy action to load the menubar"""
    return {}
