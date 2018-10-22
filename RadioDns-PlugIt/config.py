import logging
import os

from utils import safe_cast

RADIO_DNS_PORT = safe_cast(os.environ.get('RADIO_DNS_PORT', '5000'), int, 5000)

# Url to the ebu.io API.
API_URL = os.environ.get('API_URL', 'http://127.0.0.1:8000/')

# Url for the mysql connection of alchemy.
SQLALCHEMY_URL = os.environ.get('SQLALCHEMY_URL', 'mysql://root:1234@127.0.0.1:3306/radiodns')

# API secret. Random string defined by hand. To be append in the EBU.io configuration at the PlugItURI
# field. It looks something like this: http://<host>/<API_SECRET>.
API_SECRET = os.environ.get('API_SECRET', 'dev-secret')

# Amazon AWS
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '')

if AWS_ACCESS_KEY == '':
    logging.warning('AWS_ACCESS_KEY is empty.')

if AWS_SECRET_KEY == '':
    logging.warning('AWS_SECRET_KEY is empty.')

# Domain Name base for all services
DOMAIN = os.environ.get('DOMAIN', 'radio.ebu.io')

# XSI
XSISERVING_ENABLED = "True" == os.environ.get('XSISERVING_ENABLED', 'True')
XSISERVING_DOMAIN = os.environ.get('XSISERVING_DOMAIN', '127.0.0.1:5000')

# Default Service URLs for RadioDNS Services
RADIOVIS_SERVICE_DEFAULT = os.environ.get('RADIOVIS_SERVICE_DEFAULT', '127.0.0.1:5000')
RADIOEPG_SERVICE_DEFAULT = os.environ.get('RADIOEPG_SERVICE_DEFAULT', '127.0.0.1:5000')
RADIOTAG_SERVICE_DEFAULT = os.environ.get('RADIOTAG_SERVICE_DEFAULT', '127.0.0.1:5000')
RADIOTAG_ENABLED = "True" == os.environ.get('RADIOTAG_ENABLED', 'False')

# Other radio services
RADIOVIS_DNS = os.environ.get('RADIOVIS_DNS', '127.0.0.1:5000')
RADIOEPG_DNS = os.environ.get('RADIOEPG_DNS', '127.0.0.1:5000')
RADIOTAG_DNS = os.environ.get('RADIOTAG_DNS', '127.0.0.1:5000')


RADIODNS_REQUIRED_IMAGESIZES = [(32, 32), (112, 32), (128, 128), (320, 240), (600, 600)]

# wherever to enable debug mode.
DEBUG = "True" == os.environ.get('DEBUG', 'True')

# wherever the stack run without external dependencies such as AWS, EBU.IO, etc. Mostly for local testing and
# playing around.
STANDALONE = "True" == os.environ.get('STANDALONE', 'True')

# The base URL for the PlugIi API - prefix url to access utilities of this server (e.g. /radiodns/ping).
# In staging and production mode, that should be the API_SECRET.
PI_BASE_URL = os.environ.get('PI_BASE_URL', '/')

# Allowed origin for this service.
PI_ALLOWED_NETWORKS = os.environ.get('PI_ALLOWED_NETWORKS', '0.0.0.0/0').strip().split(',')

# Flask Log
FLASK_LOG_PATH = os.environ.get('FLASK_LOG_PATH', '/opt/app/flask.log')
FLASK_LOG_SIZE = safe_cast(os.environ.get('FLASK_LOG_SIZE', '10485764'), int)  # 1MB

# Url to the Sentry DNS service.
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')

# Version of this service.
PI_API_VERSION = os.environ.get('PI_API_VERSION', 'local-dev')

# Name of this service.
PI_API_NAME = os.environ.get('PI_API_NAME', 'local-dev')

# [Standalone mode only] Logo upload url. This has to point to the MockApi inside the docker network.
LOGO_INTERNAL_URL = os.environ.get('LOGO_INTERNAL_URL', 'http://127.0.0.1:8000/uploads')

# [Standalone mode only] Url of the docker host were the browser can access logos.
LOGO_PUBLIC_URL = os.environ.get('LOGO_PUBLIC_URL', 'http://127.0.0.1:8000/uploads')

# Time in seconds before reusing cache.
XML_CACHE_TIMEOUT = safe_cast(os.environ.get('XML_CACHE_TIMEOUT', '0'), int)  # in seconds
IMG_CACHE_TIMEOUT = safe_cast(os.environ.get('IMG_CACHE_TIMEOUT', '0'), int)  # in seconds

# Time during the server will try to connect to the mysql server before giving up (in seconds).
DATABASE_CONNECTION_MERCY_TIME = safe_cast(os.environ.get('DATABASE_CONNECTION_MERCY_TIME', '30'), int)
