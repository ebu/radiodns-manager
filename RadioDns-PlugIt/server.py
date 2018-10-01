#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import subprocess

import backoff
import plugit
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

import actions
import config
from db_utils import db
from models import Ecc


def db_setup():
    engine = create_engine(config.SQLALCHEMY_URL)
    logging.info("Waiting database to come online. Use CTRL + C to interrupt at any moment.")

    conn = establishConnection(engine)

    logging.info("Connection with database established")

    context = MigrationContext.configure(conn)
    heads = context.get_current_heads()
    if not len(heads) or heads[0] != context.get_current_revision():
        logging.info("Applying database evolutions, this might take a while.")
        process = subprocess.Popen("alembic upgrade head", shell=True)
        process.wait()
        db.session.add(Ecc(name="France", iso="FR", pi="f", ecc="E1"))
        db.session.commit()
        logging.info("Databases evolutions applied.")
    conn.close()


@backoff.on_exception(backoff.fibo, OperationalError, max_time=config.DATABASE_CONNECTION_MERCY_TIME)
def establishConnection(sqlalchemy_engine):
    """
    Tries to establish a connection with the database. Give up after 30 seconds.
    :param sqlalchemy_engine: The sqlalchemy engine configured for the desired database.
    :return: the connection object to the database or raise an exception after 30 seconds.
    """
    return sqlalchemy_engine.connect()


if __name__ == "__main__":
    logging.info("Starting server...")
    db_setup()

    plugit.load_actions(actions)
    plugit.app.run(host="0.0.0.0", debug=config.DEBUG, threaded=True)
