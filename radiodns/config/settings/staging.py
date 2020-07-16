"""
Production settings
- Debug - False
- AWS Integration - True
- SAML SSO Integration - True
- Sentry Integration - True
- Database - Postgress
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# STATIC
# ------------------------------------------------------------------------------
STATIC_ROOT = os.path.join(BASE_DIR, "common/static/")
STATIC_URL = "/static/"

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = False

# AWS Integration
# ------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")

# SAML Integration
# ------------------------------------------------------------------------------
USE_SAML = False
USE_LOGIN = True

SOCIAL_AUTH_SAML_SP_ENTITY_ID = env.str("SOCIAL_AUTH_SAML_SP_ENTITY_ID")
SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = env.str("SOCIAL_AUTH_SAML_SP_PUBLIC_CERT")
SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = env.str("SOCIAL_AUTH_SAML_SP_PRIVATE_KEY")
SOCIAL_AUTH_SAML_ORG_INFO = {
    "en-US": {
        "name": "radiodnsmanager",
        "displayname": "RadioDNS Manager",
        "url": "https://staging.radio.ebu.io",
    }
}
SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = {
    "givenName": "Pawel Glimos",
    "emailAddress": "pawel.glimos@bravelab.io",
}
SOCIAL_AUTH_SAML_SUPPORT_CONTACT = SOCIAL_AUTH_SAML_TECHNICAL_CONTACT


# Sentry Integration
# ------------------------------------------------------------------------------
#sentry_sdk.init(
#    dsn="https://1c5dd39283e64477a67ff2eb9260dfa2@sentry.ebu.io/18",
#    integrations=[DjangoIntegration()],
#    # If you wish to associate users to errors (assuming you are using
#    # django.contrib.auth) you may enable sending PII data.
#    send_default_pii=True,
#)

# Database
# ------------------------------------------------------------------------------
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "lpp"),
        "USER": os.environ.get("POSTGRES_USER", "root"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "1234"),
        "HOST": os.environ.get("DATABASE_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DATABASE_PORT", "5432"),
    }
}


# CORS
# ------------------------------------------------------------------------------
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True
