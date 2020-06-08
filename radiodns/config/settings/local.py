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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = os.path.join(BASE_DIR, "common/static/")

MEDIA_ROOT = os.path.join(BASE_DIR, "common/media/")

MEDIA_URL = "/media/"
