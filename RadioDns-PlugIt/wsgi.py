import os
os.chdir('/home/ubuntu/gitrepo-plugit/RadioDns-PlugIt')

from plugit import routes
import actions
import config
from plugit import app as application

if not application.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(config.FLASK_LOG_PATH,
                                       maxBytes = config.FLASK_LOG_SIZE)
    file_handler.setLevel(logging.WARNING)
    application.logger.addHandler(file_handler)

routes.load_routes(application, actions)

