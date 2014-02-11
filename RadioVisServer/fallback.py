#!/usr/bin/env python

"""The watchdog for the radiovis server.

The watch dog connect to a rabbitmq server. He check (and log) messages on every channel inside a database.

Logs greather than config.FB_LOGS_MAX_AGE are deleted.

If a channel did't recieved a message for more than config.FB_FALLBACK_TIME, (+/- config.FB_FALLBACK_CHECK), default text, link and image is send by the watchdog.

List of channels is retrived each config.FB_CHANNEL_CACHE.

"""

import config

import logging

from gevent import monkey
monkey.patch_all()


from gevent.coros import RLock
from gevent import spawn, joinall
import time

from radiodns import RadioDns
from rabbitmq import RabbitConnexion

import uuid

import sys

# API
radioDns = RadioDns()


class Fallback():
    """The main class of the watchdog"""

    def __init__(self):

        self.logger = logging.getLogger('radiovisserver.watchdog')

        # The lock to modify the list of channels
        self.channels_lock = RLock()

        # List of channels
        self.channels = []

        # Last message, by channel
        self.channels_last_message = {}

        # List of ids, by channel
        self.id_by_channel = {}

        # Init lists
        self.get_channels()

    def run(self):
        """Run all threads"""
        jobs = []

        jobs.append(spawn(self.get_channels_threads))
        jobs.append(spawn(self.connect_to_rabbitmq))
        jobs.append(spawn(self.checks_channels))
        jobs.append(spawn(self.cleanup_logs))

        joinall(jobs)

    def get_channels(self):
        """Save the list of channels"""

        self.logger.debug("Getting the list of channels...")

        new_channels = []
        new_id_by_channel = {}

        for (channel, id) in radioDns.get_all_channels():
            new_channels.append(channel)
            new_id_by_channel[channel] = id

        with self.channels_lock:
            self.channels = new_channels
            self.id_by_channel = new_id_by_channel
            self.logger.debug("Got new list of channels ! %s; %s" % (self.channels, self.id_by_channel))

    def get_channels_threads(self):
        """Thread to get the list of channels each config.FB_CHANNEL_CACHE"""

        self.logger.debug("get_channels_threads ready !")
        while True:
            time.sleep(config.FB_CHANNEL_CACHE)
            self.get_channels()

    def connect_to_rabbitmq(self):
        """Initialize the rabbitmq class"""
        self.logger.debug("Initializing the rabbitmq connection")
        self.rabbitmq = RabbitConnexion({}, self)
        joinall([spawn(self.rabbitmq.run)])

    def cleanup_logs(self):
        """Call the cleanup method each config.FB_LOGS_CLEANUP"""
        self.logger.debug("cleanup_logs started !")
        while True:
            self.logger.debug("Cleaning up logs...")
            radioDns.cleanup_logs(config.FB_LOGS_MAX_AGE)
            time.sleep(config.FB_LOGS_CLEANUP)

    def new_message(self, topic, body, bonusHeaders, when):
        """Called when a new message arrives"""
        self.logger.debug("Got message on topic %s: %s (headers: %s)" % (topic, body, bonusHeaders, ))

        gcc_topic = radioDns.convert_fm_topic_to_gcc(topic)
        # Save to mysql
        radioDns.add_log(gcc_topic, body, bonusHeaders, int(time.time()))

        # B: Update last message
        realTopic = '/'.join(gcc_topic.split('/')[:-1]) + '/'
        self.logger.debug("Real topic of %s is %s" % (topic, realTopic))

        with self.channels_lock:
            self.channels_last_message[realTopic] = when
            self.logger.debug("Last message for %s is now %s" % (realTopic, self.channels_last_message[realTopic], ))

    def checks_channels(self):
        """Check for timeout for each channels"""
        self.logger.debug("checks_channels ready !")
        while True:
            time.sleep(config.FB_FALLBACK_CHECK)

            self.logger.debug("Checking for timeouts...")

            with self.channels_lock:
                for c in self.channels:
                    if c not in self.channels_last_message or (self.channels_last_message[c] + config.FB_FALLBACK_TIME < time.time()):
                        self.logger.info("Timeout on %s !" % (c,))

                        # Get info and send emssage
                        details = radioDns.get_channel_default(self.id_by_channel[c])

                        if not details:
                            self.logger.info("No information available for %s, leaving the channel alone..." % (c,))
                        else:
                            text = details['radiotext']
                            link = details['radiolink']
                            image = config.FB_IMAGE_LOCATIONS + details['filename']

                            self.logger.info("Sending image %s with link %s and text %s on channel %s" % (image, link, text, c))

                            timestamp = str(int(time.time() * 1000))

                            headers = {'trigger-time': 'NOW', 'link': link, 'message-id': str(uuid.uuid4().int), 'topic': c + 'text', 'expires': '0', 'priority': '0', 'timestamp': timestamp}
                            self.rabbitmq.send_message(headers, "TEXT " + text)

                            headers = {'trigger-time': 'NOW', 'link': link, 'message-id': str(uuid.uuid4().int), 'topic': c + 'image', 'expires': '0', 'priority': '0', 'timestamp': timestamp}
                            self.rabbitmq.send_message(headers, "SHOW " + image)

# The logger
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger('radiovisserver')

if __name__ == '__main__':
    # Start rabbit mq client

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        config.FB_FALLBACK_CHECK = config.TEST_FB_FALLBACK_CHECK
        config.FB_FALLBACK_TIME = config.TEST_FB_FALLBACK_TIME
        config.FB_QUEUE = config.TEST_FB_QUEUE
        config.FB_LOGS_CLEANUP = config.TEST_FB_LOGS_CLEANUP

        logger.debug("Starting Fallback ! [TESTING MODE]")

    else:
        logger.debug("Starting Fallback !")

    fb = Fallback()

    joinall([spawn(fb.run)])
