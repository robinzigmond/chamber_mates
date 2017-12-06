from base import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'chambermates',
        'USER': 'django',
        'PASSWORD': 'elephant',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
