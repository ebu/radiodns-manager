import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from plugit import app as application, routes

import actions
import config
from SPI.event_listener.ORM_events_listeners import spi_generator_manager
from server import db_setup
from werkzeug.contrib.fixers import ProxyFix


def reload_pi_files():
    spi_generator_manager.tell_to_actor({"type": "add", "subject": "all", "action": "update"})


if not config.DEBUG:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(config.FLASK_LOG_PATH,
                                       maxBytes=config.FLASK_LOG_SIZE)
    file_handler.setLevel(logging.WARNING)
    application.logger.addHandler(file_handler)

routes.load_routes(application, actions)
application.wsgi_app = ProxyFix(application.wsgi_app)
db_setup()
reload_pi_files()
scheduler = BackgroundScheduler()
scheduler.add_job(reload_pi_files, "cron", day="1")
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
