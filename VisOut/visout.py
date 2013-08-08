#!/usr/bin/env python

import sys
import uuid

from gevent import monkey
monkey.patch_all()

from gevent import spawn, queue
from gevent.server import StreamServer
from gevent.coros import RLock

import time

from haigha.connection import Connection

import logging

import config

# The logger
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger('visout')
rabbitlogger = logging.getLogger('visout.rabbitmq')

# Global variable with the list of stompservers
CURRENT_STOMPSSERVERS = []

# Last message by TOPIC
LAST_MESSAGES = {}

class StompServer():
    """A basic stomp server"""

    def __init__(self, socket):
        (ip, port) = socket.getpeername()

        self.logger = logging.getLogger('visout.stompserver.' + ip + '.' + str(port))

        self.socket = socket
        # Buffer for icoming data
        self.incomingData = ''
        # Topic the client subscribled to
        self.topics = []
        # Queue of messages
        self.queue = queue.Queue()
        # Lock to send frame
        self.lock = RLock()

        # Mapping channel -> id for subscritions
        self.idsByChannels = {}

        # Mapping id- -> channel for subscritions
        self.channelsByIds = {}


    def get_frame(self):
        """Get one stomp frame"""
        
        while not "\x00" in self.incomingData:
            self.incomingData += self.socket.recv(1024)

        # Get only one frame
        splited_data = self.incomingData.split('\x00', 1)

        # Save the rest for later
        self.incomingData = splited_data[1]

        # Get command, headers and body
        frame_splited = splited_data[0].split('\n')

        command = frame_splited[0]

        headers = []
        body = ""
        headerMode = True

        for x in frame_splited[1:]:
            if x == '' and headerMode:  # Switch from headers to body
                headerMode = False
            elif headerMode:  # Add header to the lsit 
                splited_header = x.split(':', 1)
                headers.append((splited_header[0], splited_header[1]))
            else:  # Compute the body
                body += x + '\n'

        # Remove last '\n'
        body = body[:-1]

        self.logger.debug("Got one frame: %s %s %s" % (command, headers, body))

        # Return everything
        return (command, headers, body)

    def send_frame(self, command, headers, body):
        """Send a frame to the client"""

        # Lock the send, so we don't send a command inside a command
        self.logger.debug("Wait for lock to send frame: %s %s %s" % (command, headers, body))
        with self.lock:

            self.socket.send(command + '\n')
            for (header, value) in headers:
                self.socket.send(header + ':' + value + '\n')

            self.socket.send('\n')

            self.socket.send(body)

            self.socket.send('\x00')
        self.logger.debug("Frame send !")

    def consume_queue(self):
        """A thread who read topics from the queue of message and send them to the client, if requested"""
        
        try:
            while True:
                self.logger.debug("Waiting for message in queue")
                topic, message, bonusHeaders = self.queue.get()
                self.logger.debug("Got a message on topic %s: %s (headers: %s)" % (topic, message, bonusHeaders))
                
                if topic in self.topics:
                    self.logger.debug("Sending the message to the client !")
                    headers = [('destination', topic), ('message-id', str(uuid.uuid4()))]

                    for header in bonusHeaders:
                        headers.append(header)

                    # If subscribled with an ID, add the subscription header
                    if topic in self.idsByChannels:
                        headers.append(('subscription', self.idsByChannels[topic]))

                    self.send_frame("MESSAGE", headers , message)

        except Exception as e:
            self.logger.error("Error in consume_queue: %s" % (e, ))
        finally:
            self.socket.close()


    def run(self):
        """Main function to run the stompserver"""

        def get_header_value(headers, header):
            """Return the value of an header"""
            for (headerName, value) in headers:
                if headerName == header:
                    return value
            return None

        try:

            # A: Connection. Wait for a connect
            self.logger.debug("Waiting for CONNECT")
            (command, headers, body) = self.get_frame()

            if command != 'CONNECT':
                self.logger.error("Unexcepted command, %s instead of CONNECT" % (command, ))
                self.send_frame('ERROR', [('message', 'Excepted CONNECT')], '')

            # We accept any username/password, so we don't need to check them :)

            # Create a session id
            self.session_id = str(uuid.uuid4())

            self.logger.debug("Session ID is %s" % (self.session_id, ))

            # Prepase the response 
            response_headers = []

            request_id = get_header_value(headers, "request-id")
            if request_id:
                response_headers.append(('response-id', request_id))

            if get_header_value(headers, "receipt"):
                response_headers.append(('receipt-id', self.session_id))

            response_headers.append(('session', self.session_id))

            self.send_frame('CONNECTED', response_headers, '')

            self.logger.info("Stomp client connected !")

            # Spawn queue consumer
            spawn(self.consume_queue)

            # Now we just wait for a command
            while True:
                self.logger.debug("Waiting for a command")
                (command, headers, body) = self.get_frame()

                self.logger.debug("Processing command %s" % (command,))

                # Parse the command
                if command == 'DISCONNECT':
                    # Close and finish
                    self.logger.info("Client send a DISCONNECT")
                    self.socket.close()
                    return

                elif command == 'SUBSCRIBE':
                    # New subscription
                    channel = get_header_value(headers, 'destination').strip()

                    id = get_header_value(headers, 'id')

                    if id:
                        self.channelsByIds[id] = channel
                        self.idsByChannels[channel] = id

                    self.topics.append(channel)
                    self.logger.debug("Client is now subscribled to %s [ID: %s]" % (channel,id))

                    # Send the last message from the topic. A message may be send twice, but that should be ok
                    if channel in LAST_MESSAGES:
                        body, headers = LAST_MESSAGES[channel]
                        self.logger.debug("Quick sending the previous message %s (headers: %s)" % (body, headers))
                        self.queue.put((channel, body, headers))

                elif command == 'UNSUBSCRIBE':
                    # Remove subscription
                    channel = get_header_value(headers, 'destination')
                    id = get_header_value(headers, 'id')

                    if channel is None:
                        if id is None:
                            self.logger.error("Unsubscribe without channel and id !")
                        else:
                            if id not in self.channelsByIds:
                                self.logger.error("Unsubscribe with unknow id (%s)" % (id, ))
                            else:
                                channel = self.channelsByIds[id]

                    self.topics.remove(channel)

                    del self.channelsByIds[id]
                    del self.idsByChannels[channel] 


                    self.logger.debug("Client unsubscribled from %s [ID: %s]" % (channel,id))

                else:
                    self.logger.info("Unexcepted command %s %s %s" % (command, headers, body))

                # If the client want us to ack the server, ackit
                receipt = get_header_value(headers, 'receipt')
                if receipt:
                    self.logger.debug("Sending RECEIPT as requested (R-id: %s)" % (receipt,))
                    self.send_frame('RECEIPT', [('receipt-id', receipt)], '')


        except Exception as e:
            self.logger.error("Error in run: %s" % (e, ))
        finally:
            self.socket.close()


# Called when a rabbitmq message arrive
def rabbitmq_consumer(msg):
    try:
        headers = msg.properties['application_headers']

        if 'topic' in headers:
            body = msg.body
            topic = headers['topic']

            bonusHeaders = []

            # Get the list of extras headers (eg: link, trigger-time)
            for name in headers:
                if name == 'topic':  #Internal header
                    continue
                bonusHeaders.append((name, headers[name]))

            rabbitlogger.info("Got message on topic %s: %s (headers: %s)" % (topic, body, bonusHeaders))

            # Save the message as the last one
            LAST_MESSAGES[topic] = (body, bonusHeaders)

            # Broadcast message to all clients
            for c in CURRENT_STOMPSSERVERS:
                c.queue.put((topic, body, bonusHeaders))

        else:
            rabbitlogger.warning("Got message without topic: %s" % (msg, ))
    except Exception as e:
        rabbitlogger.error("Error in rabbitmq_consumer: %s", (e, ))


# Thread with connection to rabbitmq
def rabbitmq():
    
    while True:
        try:
            time.sleep(1)
            rabbitlogger.debug("Connecting to RabbitMQ (user=%s,host=%s,port=%s,vhost=%s)" % (config.RABBITMQ_USER, config.RABBITMQ_HOST, config.RABBITMQ_PORT, config.RABBITMQ_VHOST))
            cox = Connection(user=config.RABBITMQ_USER, password=config.RABBITMQ_PASSWORD, vhost=config.RABBITMQ_VHOST, host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT, debug=config.RABBITMQ_DEBUG)

            rabbitlogger.debug("Creating the channel")
            ch = cox.channel()

            # Name will come from a callback
            global queue_name
            queue_name = None

            def queue_qb(queue, msg_count, consumer_count):
                rabbitlogger.debug("Created queue %s" % (queue, ))
                global queue_name
                queue_name = queue

            rabbitlogger.debug("Creating the queue")
            ch.queue.declare(auto_delete=True, nowait=False, cb=queue_qb)

            for i in range(0, 10):  # Max 10 seconds
                if queue_name is None:
                    time.sleep(1)

            if queue_name is None:
                rabbitlogger.warning("Queue creation timeout !")
                raise Exception("Cannot create queue !")

            rabbitlogger.debug("Binding the queue")
            ch.queue.bind(queue_name, 'amq.fanout', '')

            rabbitlogger.debug("Binding the comsumer")
            ch.basic.consume(queue_name, rabbitmq_consumer)

            rabbitlogger.debug("Ready, waiting for events !")
            while True:
                if not ch.channel or (hasattr(ch.channel, '_closed') and ch.channel._closed):
                    rabbitlogger.warning("Channel is closed")
                    raise Exception("Connexion or channel closed !")
                cox.read_frames()
                    

        except Exception as e:
            rabbitlogger.error("Error in rabbitmq: %s" % (e, ))
        finally:
            cox.close()


# Handeler for new stomp clients
def stomp_client(socket, address):
    logger.info('%s:%s: New stomp connection from' % address)

    # Create a new stomp server
    s = StompServer(socket)

    # Add it to the current list
    CURRENT_STOMPSSERVERS.append(s)

    # Run the stom server
    logger.debug('%s:%s: Starting StrompServer' % address)
    s.run()

    # Connexion is now closed ! But let's do it again just in case
    logger.debug('%s:%s: StrompServer is now dead' % address)
    socket.close()

    # Remove the stomp server from the list
    CURRENT_STOMPSSERVERS.remove(s)


if __name__ == '__main__':
    # Start rabbit mq client
    logger.debug("Starting RabbitMQ connection")
    spawn(rabbitmq)

    # Start stomp server

    server = StreamServer((config.STOMP_IP, config.STOMP_PORT), stomp_client)
    logger.debug('Starting stomp server on %s:%s' % (config.STOMP_IP, config.STOMP_PORT) )
    logger.info('VisOut started !')
    server.serve_forever()