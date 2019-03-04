#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import subprocess

import backoff
import plugit
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

import actions
import config
from SPI.modules.aws_spi import AWSSPI
from SPI.modules.standalone_spi import StandaloneSPI

SPI_handler = AWSSPI() if config.USES_CDN else StandaloneSPI()


@backoff.on_exception(backoff.fibo, OperationalError, max_time=config.DATABASE_CONNECTION_MERCY_TIME)
def establish_connection(sqlalchemy_engine):
    """
    Tries to establish a connection with the database. Give up after 30 seconds.
    :param sqlalchemy_engine: The sqlalchemy engine configured for the desired database.
    :return: the connection object to the database or raise an exception after 30 seconds.
    """
    return sqlalchemy_engine.connect()


def db_setup():
    engine = create_engine(config.SQLALCHEMY_URL)
    logging.info("Waiting database to come online. Use CTRL + C to interrupt at any moment.")
    conn = None

    while conn is None:
        try:
            logging.info("Trying connection...")
            conn = establish_connection(engine)
        except OperationalError:
            logging.warning("""Couldn't connect to the server in {time} seconds to the database."""
                            .format(time=config.DATABASE_CONNECTION_MERCY_TIME))

    logging.info("Connection with database established")

    context = MigrationContext.configure(conn)
    alembic_script = ScriptDirectory.from_config(Config("./alembic.ini"))
    if context.get_current_revision() != alembic_script.get_current_head():
        logging.info("Applying database evolutions, this might take a while.")
        process = subprocess.Popen("alembic upgrade head", shell=True)
        process.wait()
        logging.info("Databases evolutions applied.")
    conn.close()


if __name__ == "__main__":
    logging.info("Starting server...")
    db_setup()

    plugit.load_actions(actions)
    plugit.app.run(host="0.0.0.0", debug=config.DEBUG, port=config.RADIO_DNS_PORT, threaded=True)
