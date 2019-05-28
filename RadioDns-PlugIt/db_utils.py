# -*- coding: utf-8 -*-

"""Utils and decorators"""
import plugit
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy

import config

plugit.app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_URL
plugit.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True


db = SQLAlchemy(plugit.app)
