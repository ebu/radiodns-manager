import config

import logging

import requests

from beaker.cache import CacheManager
import pylibmc
from beaker.util import parse_cache_config_options

import json

import sys

import socket


class RadioDns_():
    """Class to handle connection to the radioDns database: listing of topics and logins, special topic rules"""

    CACHE_DURATION = 600

    def __init__(self):
        self.logger = logging.getLogger('radiovisserver.radiodns')
        self.cache = CacheManager(**parse_cache_config_options(config.CACHE_OPTS)).get_cache('radiodns', expire=60)
        self.durablecache = pylibmc.Client(["127.0.0.1"], binary=True,
                                           behaviors={"tcp_nodelay": True,
                                                      "ketama": True})  # CacheManager(**parse_cache_config_options(config.CACHE_OPTS)).get_cache('radiodnsdurable')

    def do_query(self, url, params):
        try:
            return requests.get(config.API_URL + url, data=params).json()
        except:
            # Ommit params as it's may contain passwords
            self.logger.error("Error trying query %s" % (url, ))
            return None

    def check_auth(self, user, password, ip):
        """Check an username and password"""

        self.logger.debug("Checking username and password for %s" % (user,))

        result = self.do_query('check_auth', {'username': user, 'password': password, 'ip': ip})

        if result:
            if result['result']:
                self.logger.debug("Password ok")
                return True
            else:
                self.logger.warning("Cannot auth: %s" % (result['error'], ))
                return False
        else:
            self.logger.error("No reply when check_auth ?")
            return False

    def get_channels(self, station_id):
        """Return the list of channels for a station. Use cachinig of 1 minute"""

        self.logger.debug("Getting channels of %s" % (station_id,))

        def get_channels():
            self.logger.debug("Query channels of %s, nothing in cache !" % (station_id,))

            result = self.do_query('get_channels', {'station_id': station_id})

            if result is None:
                self.logger.error("No reply when get_channels ?")
                return []

            return result['list']

        return self.cache.get(key="get_channels-" + station_id, createfunc=get_channels)

    def update_channel_topics(self):
        """Update the channel cache from database"""
        try:
            self.logger.debug("Updating channel topic list for durable cache.")
            new_topics = []
            for (channel, id) in self.get_all_vis_channels():
                new_topics.append(channel)

            self.logger.debug(
                "Setting radiovis_channels_topics channel topic list with %s elements." % (len(new_topics)))
            self.durablecache.set('radiovis_channels_topics', new_topics, time=RadioDns.CACHE_DURATION)
        except:
            e = sys.exc_info()[0]
            self.logger.error("Error trying to update channel topics in durable cache. %s" % (e))
            return


    def contains_channel_topic(self, topic):
        """Checks if cache contains a particular channel"""
        try:
            # Normalize to ignore /image and /text
            topic = topic.rstrip('image').rstrip('text')
            channel_topics = self.durablecache.get('radiovis_channels_topics')
            return topic in channel_topics
        except:
            self.logger.error("Error trying to check channel topic %s in cache." % (topic))
            return None

    def convert_fm_topic_to_gcc(self, topic):
        """Convert a fm topic using gcc instead of country code"""
        # /topic/fm/gcc/  <=> /topic/fm/cc/ . If it's a gcc, topic[13] = '/'
        if not topic[:10] == "/topic/fm/" or topic[13] == '/':
            return topic

        self.logger.debug("Converting %s to use gcc" % (topic,))

        cachevalue = self.durablecache.get('radiovis_isoecc_' + topic)
        if cachevalue:
            return cachevalue

        def convert_topic():

            splited_topic = topic.split('/')

            cc = splited_topic[3]

            self.logger.debug("Querying gcc value for %s, nothing in cache !" % (cc,))

            result = self.do_query('get_gcc', {'cc': cc})
            if result is None:
                self.logger.error("No reply when convert_fm_topic_to_gcc ?")
                return topic  # Return the topic

            splited_topic[3] = result['gcc']

            gcc_topic = '/'.join(splited_topic)

            self.logger.debug("Setting radiovis_isoecc_ to durable cache topic list with %s." % (gcc_topic))
            self.durablecache.set('radiovis_isoecc_' + topic, gcc_topic, time=RadioDns.CACHE_DURATION)
            return gcc_topic

        return self.cache.get(key='topic-to-gcc-' + topic, createfunc=convert_topic)

    def check_special_matchs(self, topic, topics):
        """Return true if topic is in the list of topics, using specials rules (eg. fm)"""

        # Only a special rule for fm
        if not topic[:10] == "/topic/fm/":
            return None

        # Check matches using gcc version
        topic = self.convert_fm_topic_to_gcc(topic)

        for subTopic in topics:
            subTopicConverted = self.convert_fm_topic_to_gcc(subTopic)
            if subTopicConverted == topic:
                return subTopic

        return None

    def get_all_channels(self):
        """Return the list of all channels"""

        result = self.do_query('get_all_channels', {})

        if result is None:
            self.logger.error("No reply when get_all_channels ?")
            return []

        retour = []

        for (topic, id) in result['list']:
            retour.append((self.convert_fm_topic_to_gcc(topic), id))

        return retour

    def get_all_vis_channels(self):
        """Return the list of all VIS channel that have an image"""

        result = self.do_query('get_all_vis_channels', {})

        if result is None:
            self.logger.error("No reply when get_all_vis_channels ?")
            return []

        retour = []

        for (topic, id) in result['list']:
            retour.append((self.convert_fm_topic_to_gcc(topic), id))

        return retour

    def get_channel_default(self, id):
        """Return the default image, link and message for a channel"""

        # Get out of cache if available
        cachevalue = self.durablecache.get('get_channel_default_' + str(id))
        if cachevalue:
            return cachevalue

        result = self.do_query('get_channel_default', {'id': id})

        if result is None:
            self.logger.error("No reply when get_channel_default %s ?" % (id, ))
            return []

        # Save to cache
        self.durablecache.set('get_channel_default_' + str(id), result['info'], time=RadioDns.CACHE_DURATION)

        return result['info']

    def add_log(self, topic, message, headers, timestamp):
        """Add a log entry"""

        result = self.do_query('add_log', {'topic': topic, 'message': str(message), 'headers': json.dumps(headers),
                                           'timestamp': timestamp})

        if result is None:
            self.logger.error("No reply when add_log %s %s %s %s ?" % (topic, message, headers, timestamp, ))

    def cleanup_logs(self, max_age):
        """Clean logs"""
        result = self.do_query('cleanup_logs', {'max_age': max_age})

        if result is None:
            self.logger.error("No reply when cleanup_logs ?")


class RadioDnsTesting(RadioDns_):
    """Special class for testing"""

    def do_query(self, url, params):
        """Never do a real query but act as we're the api !"""

        result = {}

        if url == 'check_auth':

            # Authentification: test:test or testip:<theip>

            result['error'] = ''
            if params['username'] == "2.testip":
                result['result'] = params['ip'] == params['password']
            else:
                result['result'] = params['username'][2:] == "test" and params['password'] == "test"

        elif url == 'get_channels':

            # List of allowed channels
            if params['station_id'] == '1':  # Normal tests
                result['list'] = config.TEST_TOPICS
            elif params['station_id'] == '3':  # GCC/CC tests
                result['list'] = [config.TEST_ECC_TOPIC_GCC, config.TEST_ECC_TOPIC_CC]
            elif params['station_id'] == '4':  # Watchdog test
                result['list'] = [config.TEST_WATCHDOG_TOPIC[0][0]]
            else:
                result['list'] = []

        elif url == 'get_gcc':

            if params['cc'] in config.TEST_ECC:
                result['gcc'] = config.TEST_ECC[params['cc']]

        elif url == 'get_all_channels':
            result['list'] = config.TEST_WATCHDOG_TOPIC
        elif url == 'get_channel_default':
            result['info'] = {}
            if params['id'] == 1:
                result['info'] = config.TEST_CHANNEL_DEFAULT
        elif url == 'add_log':
            params['type'] = 'log'
            data = json.dumps(params)
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(data, ('127.0.0.1', 61422))
        elif url == 'cleanup_logs':
            params['type'] = 'cleanup_logs'
            data = json.dumps(params)
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(data, ('127.0.0.1', 61422))
        else:
            raise NotImplementedError("Not implemented query %s" % (url,))

        return result


if len(sys.argv) > 1 and sys.argv[1] == '--test':
    RadioDns = RadioDnsTesting
else:
    RadioDns = RadioDns_
