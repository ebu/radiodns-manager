import logging
import os

RADIO_DNS_PORT = int(os.environ.get('RADIO_DNS_PORT', '5000'))

# Url to the ebu.io API.
API_URL = os.environ.get('API_URL', 'http://127.0.0.1:4000/')

# Url for the mysql connection of alchemy.
SQLALCHEMY_URL = os.environ.get('SQLALCHEMY_URL', 'mysql://root:1234@127.0.0.1:3306/radiodns')

# API secret. Random string defined by hand. To be append in the EBU.io configuration at the PlugItURI
# field. It looks something like this: http://<host>/<API_SECRET>/.
API_SECRET = os.environ.get('API_SECRET', 'dev-secret')

# Amazon AWS
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '')
AWS_ZONE = os.environ.get('AWS_ZONE', 'eu-west-1')

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
RADIOVIS_DNS = os.environ.get('RADIOVIS_DNS', '127.0.0.1')
RADIOEPG_DNS = os.environ.get('RADIOEPG_DNS', '127.0.0.1')
RADIOTAG_DNS = os.environ.get('RADIOTAG_DNS', '127.0.0.1')
RADIOSPI_DNS = os.environ.get('RADIOSPI_DNS', '127.0.0.1')

RADIOVIS_PORT = os.environ.get('RADIOVIS_PORT', '61613')
RADIOEPG_PORT = os.environ.get('RADIOEPG_PORT', '5000')
RADIOTAG_PORT = os.environ.get('RADIOTAG_PORT', '5000')
RADIOSPI_PORT = os.environ.get('RADIOSPI_PORT', '5000')

RADIOVIS_SERVICE_DEFAULT = RADIOVIS_DNS + ":" + RADIOVIS_PORT
RADIOEPG_SERVICE_DEFAULT = RADIOEPG_DNS + ":" + RADIOEPG_PORT
RADIOTAG_SERVICE_DEFAULT = RADIOTAG_DNS + ":" + RADIOTAG_PORT
RADIOSPI_SERVICE_DEFAULT = RADIOSPI_DNS + ":" + RADIOSPI_PORT
RADIOTAG_ENABLED = "True" == os.environ.get('RADIOTAG_ENABLED', 'False')

RADIODNS_REQUIRED_IMAGESIZES = [(32, 32), (112, 32), (128, 128), (320, 240), (600, 600)]

# wherever to enable debug mode.
DEBUG = "True" == os.environ.get('DEBUG', 'True')

# wherever the app should run without external dependencies such as AWS, EBU.IO, etc. Mostly for local testing.
STANDALONE = "True" == os.environ.get('STANDALONE', 'True')

# The base URL for the PlugIi API - prefix url to access utilities of this server (e.g. /radiodns/ping).
# In production mode, that should be the API_SECRET.
PI_BASE_URL = os.environ.get('PI_BASE_URL', '/dev-secret/')

# Allowed hosts for this service. List of hosts commas separated.
PI_ALLOWED_NETWORKS = os.environ.get('PI_ALLOWED_NETWORKS', '0.0.0.0/0').strip().split(',')

# Flask Log
FLASK_LOG_PATH = os.environ.get('FLASK_LOG_PATH', '/opt/app/flask.log')
FLASK_LOG_SIZE = int(os.environ.get('FLASK_LOG_SIZE', '10485764'))  # 1MB

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

# Time in seconds before discarding cache.
XML_CACHE_TIMEOUT = int(os.environ.get('XML_CACHE_TIMEOUT', '0'))  # in seconds
IMG_CACHE_TIMEOUT = int(os.environ.get('IMG_CACHE_TIMEOUT', '0'))  # in seconds

# Time during the server will try to connect to the mysql server before giving up (in seconds).
DATABASE_CONNECTION_MERCY_TIME = int(os.environ.get('DATABASE_CONNECTION_MERCY_TIME', '30'))

# Endpoint to the VIS player of radiodns manager. Used by the HTML vis player.
VIS_WEB_SOCKET_ENDPOINT_HOST = os.environ.get('VIS_WEB_SOCKET_ENDPOINT_HOST', '127.0.0.1')

# Current Revision.
REVISION = "dev-local"

# If you want to use the aws cloudfront integration to deliver spi files.
USES_CDN = "True" == os.environ.get('USES_CDN', 'False')

# Name of the aws bucket that will serve static SPI files.
SPI_BUCKET_NAME = os.environ.get('SPI_BUCKET_NAME', 'SPISTATIC').lower()

# Number of seconds between each generation of spi file if any is to be made.
SPI_GENERATION_INTERVAL = int(os.environ.get('SPI_GENERATION_INTERVAL', '300'))

SPI_CLOUDFRONT_DOMAIN = os.environ.get("SPI_CLOUDFRONT_DOMAIN", "CHANGEME.cloudfront.net")
