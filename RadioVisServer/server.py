#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()

from gevent import spawn
from gevent.server import StreamServer

import logging

import config

from stomp import StompServer

from rabbitmq import RabbitConnexion

# The logger
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger('radiovisserver')


# Last message by TOPIC
LAST_MESSAGES = {}

# Create the class to manage the rabbit connexion
rabbitcox = RabbitConnexion(LAST_MESSAGES)


# Handeler for new stomp clients
def stomp_client(socket, address):
    logger.info('%s:%s: New stomp connection from' % address)

    # Create a new stomp server
    s = StompServer(socket, LAST_MESSAGES, rabbitcox)

    # Let rabbitmq send messages to the stomp server
    rabbitcox.add_stomp_server(s)

    # Run the stom server
    logger.debug('%s:%s: Starting StrompServer' % address)
    s.run()

    # Connexion is now closed ! But let's do it again just in case
    logger.debug('%s:%s: StrompServer is now dead' % address)
    socket.close()

    # Stop managing the stom server
    rabbitcox.remove_stomp_server(s)


if __name__ == '__main__':
    # Start rabbit mq client
    logger.debug("Starting RabbitMQ connection")
    spawn(rabbitcox.run)

    # Start stomp server
    server = StreamServer((config.STOMP_IP, config.STOMP_PORT), stomp_client)
    logger.debug('Starting stomp server on %s:%s' % (config.STOMP_IP, config.STOMP_PORT) )
    logger.info('RadioVis server started !')
    server.serve_forever()
