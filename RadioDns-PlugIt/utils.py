# -*- coding: utf-8 -*-

"""Utils and decorators"""

import config
import os
import sys

# Database: This loads the DB differently depending on what we are
# running (plugit/flask server or standalone)

if 'plugit' in sys.modules:
    # We are running in the plugit server. Import its DB
    from plugit import db
else:
    # Create db here
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask import Flask
    # FIXME this is just a hack
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)