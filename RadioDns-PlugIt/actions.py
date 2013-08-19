# -*- coding: utf-8 -*-

# Include main methods
from main.actions import *

# Include stations methods
from stations.actions import *

# Include channls methods
from channels.actions import *

# Include radiovis methods
from radiovis.actions import *

# Include radioepg methods
from radioepg.actions import *

from utils import action


@action(route="/menubar", template="menubar.html")
def menubar(request):
    """Dummy action to load the menubar"""
    return {}
