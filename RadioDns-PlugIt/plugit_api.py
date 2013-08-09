"""Tools to access the PlugIt API"""

import requests

class PlugItAPI():
	"""Main instance to access plugit api"""

	def __init__(self, url):
		"""Create a new PlugItAPI instance, need url as the main endpoint for the API"""
		self.url = url

	def _request(self, uri, params=None, postParams=None, verb='GET'):
		"""Execute a request on the plugit api"""
		return getattr(requests, verb.lower())(self.url + uri, params=params, data=postParams, stream=True)

	def get_user(self, userPk):
		"""Return an user speficied with userPk"""
		r = self._request('user/' + userPk)
		if not r:
			return None

		# Base properties
		u = User()
		u.pk = userPk
		u.id = userPk

		# Copy data inside the user
		data = r.json()

		for attr in data:
			setattr(u, attr, data[attr])

		return u

	def get_orga(self, orgaPk):
		"""Return an organization speficied with orgaPk"""
		r = self._request('orga/' + orgaPk)
		if not r:
			return None

		# Base properties
		o = Orga()
		o.pk = orgaPk
		o.id = orgaPk

		# Copy data inside the orga
		data = r.json()

		for attr in data:
			setattr(o, attr, data[attr])

		return o


class User():
	"""Represent an user"""

class Orga():
	"""Represent an organization"""
