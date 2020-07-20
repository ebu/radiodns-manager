"""
Local settings
- Debug - True
- AWS Integration - False
- SAML SSO Integration - False
- Sentry Integration - False
- Database - Django default - SQLite
"""

from .base import *


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)

# CORS
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env.str(
    "DJANGO_SECRET_KEY", default="m#q+a$jnttg@-d(7n&s$2yccwutx=r95-4may*5*myxwda%o-x"
)

# SAML
# ------------------------------------------------------------------------------
USE_SAML = False
USE_LOGIN = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = "/common/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "common/static/")

# Media files - uploaded images
# https://docs.djangoproject.com/en/3.0/howto/static-files/
MEDIA_ROOT = os.path.join(BASE_DIR, "common/media/")
MEDIA_URL = "/media/"
