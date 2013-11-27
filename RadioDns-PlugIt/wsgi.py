import os
os.chdir('/home/ubuntu/gitrepo-plugit/RadioDns-PlugIt')

from plugit import routes
import actions
from plugit import app as application

routes.load_routes(application, actions)
