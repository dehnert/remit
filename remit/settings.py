# Django settings for treasury project.
import os
import sys

SITE_ROOT = os.path.normpath(os.path.dirname(__file__))
SITE_WEB_PATH = ''
DEFAULT_DOMAIN = 'mit.edu'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Remit team', 'remit@mit.edu'),
)
SERVER_EMAIL = 'remit@mit.edu'
USE_CERTS = True

GROUP_NAME = 'Remit'
SIGNATORY_EMAIL = None

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.path.join(SITE_ROOT, 'treasury.sqlite')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

from local_settings import *

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = SITE_ROOT + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = SITE_WEB_PATH + '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = SITE_WEB_PATH + '/media/admin/'

LOGIN_REDIRECT_URL  = SITE_WEB_PATH + '/accounts/profile'
LOGIN_URL  = SITE_WEB_PATH + '/accounts/login'
LOGOUT_URL = SITE_WEB_PATH + '/accounts/logout'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #http://docs.djangoproject.com/en/dev/howto/auth-remote-user/
    #'django.contrib.auth.middleware.RemoteUserMiddleware',
    'mit.ScriptsRemoteUserMiddleware',
)

if USE_CERTS:
    AUTHENTICATION_BACKENDS = (
        'mit.ScriptsRemoteUserBackend',
    )
else:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )

ROOT_URLCONF = 'remit.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    SITE_ROOT + '/templates/',
    SITE_ROOT + '/remit_templates/',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'treebeard',
    'vouchers',
    'finance_core',
    'util',
)

from local_settings_after import *
