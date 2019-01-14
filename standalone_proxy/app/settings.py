# -*- coding: utf-8 -*-

import os
from os.path import abspath, dirname, join, normpath


# Django settings for PlugIt project.
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                       # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                       # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                       # Set to empty string for default.
    }
}


DJANGO_ROOT = dirname(abspath(__file__)) + '/../'

# Default Test Runner, necessary since Django 1.6
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media')) + '/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = normpath(join(MEDIA_ROOT, 'static')) + '/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/media/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    normpath(join(DJANGO_ROOT, 'static')) + '/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'app.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'app.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    normpath(join(DJANGO_ROOT, 'templates')) + '/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'plugIt',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'The game. Please also replace this string.'

PIAPI_STANDALONE = True
PIAPI_STANDALONE_URI = os.environ.get('PLUGIT_SERVER', 'http://127.0.0.1:5000/dev-secret')
PIAPI_BASEURI = os.environ.get('PLUGIT_SERVER_BASEURI', '/plugIt/')
PIAPI_USERDATA = ['username', 'id', 'pk', 'first_name', 'last_name', 'email', 'ebuio_member', 'ebuio_admin', 'ebuio_orga_member', 'ebuio_orga_admin']
PIAPI_ORGAMODE = True  # Don't active this with PIAPI_REALUSERS !
PIAPI_REALUSERS = False  # Don't active this with PIAPI_ORGAMODE !
PIAPI_PLUGITMENUACTION = 'menubar'
PIAPI_PLUGITTEMPLATE = 'plugItBase-menu.html'  # One out of 'plugItBase.html', 'plugItBase-menu.html'

HONOR_X_FORWARDED_FOR = False  # Use `X-Forwarded-For` ip for `X-PlugIt-Remote-Addr` (if you're behind a proxy that may be useful)

PIAPI_PROXYMODE = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.TemporaryFileUploadHandler",)

LOGIN_REDIRECT_URL = '/'

MAIL_SENDER = 'no-reply@ebu.io'

EBUIO_MAIL_SECRET_HASH = 'CHANGE_ME'
EBUIO_MAIL_SECRET_KEY = 'CHANGE_ME'

INCOMING_MAIL_USER = ''
INCOMING_MAIL_PASSWORD = ''
INCOMING_MAIL_HOST = ''

DISCUSSION_ID = 'I-D'
