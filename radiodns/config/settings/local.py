"""
Local settings
- Run in Debug mode
"""

from .base import *


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY", default="m#q+a$jnttg@-d(7n&s$2yccwutx=r95-4may*5*myxwda%o-x"
)

USE_SAML = False
USE_LOGIN = True
