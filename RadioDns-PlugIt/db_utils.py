# -*- coding: utf-8 -*-

"""Utils and decorators"""
import plugit
from flask_sqlalchemy import SQLAlchemy

import config

plugit.app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_URL
plugit.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(plugit.app)
