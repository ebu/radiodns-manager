#!/usr/bin/env python

"""Main file for the radiovis server.

The RadioVis server handle stomp connections from clients (radios or content managers) and take care of forwarding messages.

"""

from gevent import monkey
monkey.patch_all()

from gevent import spawn
from gevent.server import StreamServer

import logging

from monitoring import Monitoring

import config

from stomp import StompServer

from rabbitmq import RabbitConnexion

import sys

# The logger
logging.basicConfig(format="[%(levelname)s] %(asctime)-15s - %(message)s", level=config.LOG_LEVEL)
logger = logging.getLogger('radiovisserver')
# Logging to file is handled outside by supvervisord instead of the application itself
# fh = FileHandler(filename='radiovis-server.log', mode='a')
# fh.setFormatter(Formatter(fmt="[%(levelname)s] %(asctime)-15s - %(message)s"))
# logger.addHandler(fh)


# Last message by TOPIC
LAST_MESSAGES = {}


monitoring = Monitoring()
monitoring.count("radiovis.global.servers")

# Create the class to manage the rabbit connexion
rabbitcox = RabbitConnexion(LAST_MESSAGES, monitoring)


# Handeler for new stomp clients
def stomp_client(socket, address):
    logger.info('%s:%s: New stomp connection from' % address)

    # Create a new stomp server
    s = StompServer(socket, LAST_MESSAGES, rabbitcox, monitoring)
    monitoring.count("radiovis.global.connections", {"session_id": s.session_id, "ip": s.info_ip + ':' + str(s.info_port) })

    # Let rabbitmq send messages to the stomp server
    rabbitcox.add_stomp_server(s)

    # Run the stomp server
    logger.debug('%s:%s: Starting StompServer' % address)
    s.run()

    monitoring.count("radiovis.global.disconnections", {"session_id": s.session_id, "ip": s.info_ip + ':' + str(s.info_port) })

    # Connexion is now closed ! But let's do it again just in case
    logger.debug('%s:%s: StompServer is now dead' % address)
    socket.close()

    # Stop managing the stom server
    rabbitcox.remove_stomp_server(s)

    # Tell the server to stop, just in case.
    s.sucide = True

    del s.queue
    del s


if __name__ == '__main__':
    # Start rabbit mq client
    logger.debug("Starting RabbitMQ connection")
    spawn(monitoring.run)
    spawn(rabbitcox.run)

    # Start stomp server
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        server = StreamServer(('127.0.0.1', 61424), stomp_client)
        logger.debug('Starting stomp server on %s:%s [TESTMODE!]' % ('127.0.0.1', 61424))

    else:
        server = StreamServer((config.STOMP_IP, config.STOMP_PORT), stomp_client)
        logger.debug('Starting stomp server on %s:%s' % (config.STOMP_IP, config.STOMP_PORT))

    server.serve_forever()
    logger.info('RadioVis server started !')

