import os

_site_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : os.path.join(_site_root, 'db.sqlite'),
    },
}

SITE_URL_BASE = "http://localhost:8006" # you may wish to change the port

# Mail sending
# See https://docs.djangoproject.com/en/dev/topics/email/#email-backends

# Display intermixed with the error messages
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Make this unique, and don't share it with anybody.
#SECRET_KEY = something
# Generate the "something" with:
# import random; ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789@#%&-_=+') for i in range(50)])

SESSION_COOKIE_SECURE = False

DEBUG = False
DEBUG = True
