from haigha.connection import Connection

import logging
import time

import config
import sys

from haigha.message import Message

import statsd

from radiodns import RadioDns
radioDns = RadioDns()


class RabbitConnexion():
    """Manage connexion to Rabbit"""

    def __init__(self, LAST_MESSAGES, watchdog=None):
        self.logger = logging.getLogger('radiovisserver.rabbitmq')

        # List of stompservers
        self.stompservers = []

        # Save LAST_MESSAGES
        self.LAST_MESSAGES = LAST_MESSAGES

        # Save the watchdog
        self.watchdog = watchdog

        # The global gauge
        self.gauge = statsd.Gauge(config.STATS_GAUGE_APPNAME)

    def consumer(self, msg):
        """Called when a rabbitmq message arrive"""

        try:
            headers = msg.properties['application_headers']

            if 'topic' in headers:
                body = msg.body
                topic = headers['topic']

                bonusHeaders = []

                # Get the list of extras headers (eg: link, trigger-time)
                for name in headers:
                    if name == 'topic':  # Internal header
                        continue
                    bonusHeaders.append((name, headers[name]))

                self.logger.info("Got message on topic %s: %s (headers: %s)" % (topic, body, bonusHeaders))

                if self.watchdog:  # If we are the watchdog, send stats
                    statsd.Counter(config.STATS_COUNTER_NBMESSAGE_RECV + '.'.join(topic.split('/'))).increment()

                # Save the message as the last one
                converted_topic = radioDns.convert_fm_topic_to_gcc(topic)
                self.LAST_MESSAGES[converted_topic] = (body, bonusHeaders)

                # Broadcast message to all clients
                for c in self.stompservers:
                    c.new_message(topic, body, bonusHeaders)

                # Inform the watchdog
                if self.watchdog:
                    self.watchdog.new_message(topic, body, bonusHeaders, int(headers['when']))

            else:
                self.logger.warning("Got message without topic: %s" % (msg, ))
        except Exception as e:
            self.logger.error("Error in consumer: %s", (e, ))

    def run(self):
        """Thread with connection to rabbitmq"""

        if config.RABBITMQ_LOOPBACK:
            self.logger.warning("Looopback mode: No connection, waiting for ever...")
            while True:
                time.sleep(1)

        while True:
            try:
                time.sleep(1)
                self.logger.debug("Connecting to RabbitMQ (user=%s,host=%s,port=%s,vhost=%s)" % (config.RABBITMQ_USER, config.RABBITMQ_HOST, config.RABBITMQ_PORT, config.RABBITMQ_VHOST))
                self.cox = Connection(user=config.RABBITMQ_USER, password=config.RABBITMQ_PASSWORD, vhost=config.RABBITMQ_VHOST, host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT, debug=config.RABBITMQ_DEBUG)

                self.logger.debug("Creating the channel")
                self.ch = self.cox.channel()

                # Name will come from a callback
                global queue_name
                queue_name = None

                def queue_qb(queue, msg_count, consumer_count):
                    self.logger.debug("Created queue %s" % (queue, ))
                    global queue_name
                    queue_name = queue

                self.logger.debug("Creating the queue")
                if not self.watchdog:
                    # 'Normal', tempory queue
                    self.ch.queue.declare(auto_delete=True, nowait=False, cb=queue_qb)
                else:
                    # Persistant queue, if not in test mode
                    if len(sys.argv) > 1 and sys.argv[1] == '--test':
                        self.ch.queue.declare(config.FB_QUEUE, auto_delete=True, nowait=False, cb=queue_qb)
                    else:
                        self.ch.queue.declare(config.FB_QUEUE, auto_delete=False, nowait=False, cb=queue_qb)

                for i in range(0, 10):  # Max 10 seconds
                    if queue_name is None:
                        time.sleep(1)

                if queue_name is None:
                    self.logger.warning("Queue creation timeout !")
                    raise Exception("Cannot create queue !")

                self.logger.debug("Binding the exchange %s" % (config.RABBITMQ_EXCHANGE, ))
                self.ch.queue.bind(queue_name, config.RABBITMQ_EXCHANGE, '')

                self.logger.debug("Binding the comsumer")
                self.ch.basic.consume(queue_name, self.consumer)

                self.logger.debug("Ready, waiting for events !")
                while True:
                    if not hasattr(self.ch, 'channel') or (hasattr(self.ch.channel, '_closed') and self.ch.channel._closed):
                        self.logger.warning("Channel is closed")
                        raise Exception("Connexion or channel closed !")
                    self.cox.read_frames()

            except Exception as e:
                self.logger.error("Error in run: %s" % (e, ))
            finally:
                self.cox.close()

    def send_message(self, headers, message):
        """Send a message to the queue"""

        # Append current ts
        headers['when'] = str(int(time.time()))

        self.logger.info("Sending message (with headers %s) %s to %s" % (headers, message, config.RABBITMQ_EXCHANGE))

        if self.watchdog:
            statsd.Counter(config.STATS_COUNTER_NBMESSAGE_SEND + '.'.join(headers['topic'].split('/'))).increment()
        else:
            statsd.Counter(config.STATS_COUNTER_NBMESSAGE_SEND_BY_WATCHDOG + '.'.join(headers['topic'].split('/'))).increment()

        if config.RABBITMQ_LOOPBACK:
            self.logger.info("Sending using loopback, calling function directly")

            class FalseMsg():
                def __init__(self, body, headers):
                    self.body = body
                    self.properties = {'application_headers': headers}

            self.consumer(FalseMsg(message, headers))

        else:
            self.ch.basic.publish(Message(message, application_headers=headers), config.RABBITMQ_EXCHANGE, '')

    def add_stomp_server(self, s):
        """Handle a new stomp server"""
        self.stompservers.append(s)
        self.update_stats()

    def remove_stomp_server(self, s):
        """Stop handeling a stomp server"""
        self.stompservers.remove(s)
        self.update_stats()

    def update_stats(self):
        """Update stats"""
        self.gauge.send(config.STATS_GAUGE_NB_CLIENTS, len(self.stompservers))
