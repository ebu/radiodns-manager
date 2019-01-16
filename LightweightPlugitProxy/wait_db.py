import logging
from time import sleep

import backoff
import psycopg2
import os

DATABASE_CONNECTION_MERCY_TIME = int(os.environ.get("DATABASE_CONNECTION_MERCY_TIME", "60"))


@backoff.on_exception(
    backoff.fibo,
    psycopg2.OperationalError,
    max_time=DATABASE_CONNECTION_MERCY_TIME,
)
def establish_connection():
    """
    Tries to establish a connection with the database. Give up after 30 seconds.
    :return: the connection object to the database or raise an exception after 30 seconds.
    """
    return psycopg2.connect(
            host=os.environ.get("DATABASE_HOST", "127.0.0.1"),
            user=os.environ.get("POSTGRES_USER", "root"),
            password=os.environ.get("DATABASE_PASSWORD", "1234"),
            dbname=os.environ.get("DATABASE_NAME", "lpp"),
            port=os.environ.get("DATABASE_PORT", "5432"),
        )


conn = None
while conn is None:
    try:
        logging.info("Trying connection...")
        conn = establish_connection()
    except psycopg2.OperationalError:
        logging.warning("""Couldn't connect to the server in {time} seconds to the database."""
                        .format(time=DATABASE_CONNECTION_MERCY_TIME))

    logging.info("Connection with database established")

conn.close()
