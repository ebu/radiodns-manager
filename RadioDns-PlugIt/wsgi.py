from plugit import app as application, routes

import actions
import config
from server import db_setup

if not config.DEBUG:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(config.FLASK_LOG_PATH,
                                       maxBytes=config.FLASK_LOG_SIZE)
    file_handler.setLevel(logging.WARNING)
    application.logger.addHandler(file_handler)

routes.load_routes(application, actions)
db_setup()

