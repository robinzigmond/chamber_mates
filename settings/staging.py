import dj_database_url
from base import *

DEBUG = False

# Log DEBUG information to the console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}

DATABASES["default"] = dj_database_url.config()
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
