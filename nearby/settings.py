"""
Django settings for the ward councillor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'true') == 'true'

# SECURITY WARNING: keep the secret key used in production secret!
if DEBUG:
    SECRET_KEY = '-r&cjf5&l80y&(q_fiidd$-u7&o$=gv)s84=2^a2$o^&9aco0o'
else:
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

IEC_API_USERNAME = os.environ['IEC_API_USERNAME']
IEC_API_PASSWORD = os.environ['IEC_API_PASSWORD']

GOOGLE_ANALYTICS_ID = 'UA-48399585-22'


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pipeline',
    'django_extensions',
    'memoize',

    'nearby',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nearby.urls'

WSGI_APPLICATION = 'nearby.wsgi.application'

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
import dj_database_url
db_config = dj_database_url.config(default='postgresql://nearby:nearby@localhost:5432/nearby')
db_config['ATOMIC_REQUESTS'] = True
DATABASES = {
    'default': db_config,
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Email
ADMINS = [('Code4SA', 'webapps@code4sa.org')]
DEFAULT_FROM_EMAIL = ADMINS[0][1]
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_SUBJECT_PREFIX = '[Nearby] '
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_HOST_USER = 'webapps@code4sa.org'
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587


# Caches
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
        },
    }
# IEC api cache for when their API is down
CACHES['iec'] = {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'iec_cache',
    'OPTIONS': {
        'MAX_ENTRIES': 5000,  # about 4000 wards in SA
    },
}

# Google sheets
GOOGLE_SHEETS_EMAIL = os.environ.get('GOOGLE_SHEETS_EMAIL')
GOOGLE_SHEETS_PRIVATE_KEY = os.environ.get('GOOGLE_SHEETS_PRIVATE_KEY')
GOOGLE_SHEETS_SHEET_KEY = "1rtez8t8MGtG7vTQe-wyCrIgsgejwddoshrPkYPECC7E"

# if DEBUG:
#     import ssl
#     _create_unverified_https_context = ssl._create_unverified_context
#     ssl._create_default_https_context = _create_unverified_https_context


# Templates
TEMPLATE_DEBUG = DEBUG
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "nearby.context_processors.google_analytics",
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

ASSETS_DEBUG = DEBUG
ASSETS_URL_EXPIRE = False

# assets must be placed in the 'static' dir of your Django app

# where the compiled assets go
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# the URL for assets
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "pipeline.finders.PipelineFinder",
)

PYSCSS_LOAD_PATHS = [
    os.path.join(BASE_DIR, 'nearby', 'static'),
    os.path.join(BASE_DIR, 'nearby', 'static', 'bower_components'),
]

PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'bower_components/code4sa-styles/css/code4sa-custom-bootstrap.css',
            'bower_components/fontawesome/css/font-awesome.css',
            'stylesheets/leaflet.css',
            'stylesheets/app.scss',
        ),
        'output_filename': 'app.css',
    },
}
PIPELINE_JS = {
    'js': {
        'source_filenames': (
            'bower_components/jquery/dist/jquery.min.js',
            'bower_components/code4sa-styles/js/bootstrap.min.js',
            'javascript/leaflet.js',
            'javascript/pym.min.js',
            'javascript/app.js',
        ),
        'output_filename': 'app.js',
    },
    'nearby-embed-js': {
        'source_filenames': (
            'javascript/pym.min.js',
            'javascript/councillor-embed.js',
        ),
        'output_filename': 'councillor-embed.js',
    },
}
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

PIPELINE_COMPILERS = (
    'nearby.pipeline.PyScssCompiler',
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'nearby.pipeline.GzipManifestPipelineStorage'


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR'
    },
    'loggers': {
        'nearby': {
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django': {
            'level': 'DEBUG' if DEBUG else 'INFO',
        }
    }
}
