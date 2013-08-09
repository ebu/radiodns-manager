import config

import logging

import requests

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options



class RadioDns():
	"""Class to handle connection to the radioDns database: listing of topics and logins"""

	def __init__(self):
		self.logger = logging.getLogger('radiovisserver.radiodns')
		self.cache = CacheManager(**parse_cache_config_options(config.CACHE_OPTS)).get_cache('radiodns', expire=60)

	def do_query(self, url, params):
		try:
			return requests.get(config.API_URL + url, data=params).json()
		except:
			# Ommit params as it's may contain passwords
			self.logger.error("Error trying query %s" % (url, ))
			return None

	def check_auth(self, user, password):
		"""Check an username and password"""

		self.logger.debug("Checking username and password for %s" % (user,))

		result = self.do_query('check_auth', {'username': user, 'password': password})

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