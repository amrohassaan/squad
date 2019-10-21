"""
Django settings for squad project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from celery.schedules import crontab
from django.conf import global_settings
from email.utils import parseaddr
from glob import glob
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = BASE_DIR
if not os.access(DATA_DIR, os.W_OK):
    # cannot write to source tree
    DATA_DIR = os.path.join(
        os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share')),
        'squad',
    )
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
secret_key_file = os.getenv('SECRET_KEY_FILE', None)
if secret_key_file is None:
    secret_key_file = os.path.join(DATA_DIR, 'secret.dat')

if not os.path.exists(secret_key_file):
    from squad.core.utils import random_key
    fd = os.open(secret_key_file, os.O_WRONLY | os.O_CREAT, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(random_key(64))

SECRET_KEY = open(secret_key_file).read()

DEBUG = os.getenv('ENV') != 'production'

ALLOWED_HOSTS = ['*']


# Application definition

try:
    import imp
    imp.find_module('django_extensions')
    django_extensions = 'django_extensions'
except ImportError:
    django_extensions = None


__apps__ = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'corsheaders',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    django_extensions,  # OPTIONAL
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_filters',
    'simple_history',
    'django_filters',
    'crispy_forms',
    'squad.core',
    'squad.api',
    'squad.frontend',
    'squad.ci',
]

INSTALLED_APPS = [app for app in __apps__ if app]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'squad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        # look for templates explicitly under squad.api so that Django REST
        # Framework finds rest_framework/api.html in there
        'DIRS': [os.path.join(BASE_DIR, path) for path in ['squad/frontend/templates', 'squad/core/templates', 'squad/ci/templates']],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'squad.jinja2.environment',
            'extensions': ['jinja2.ext.i18n', 'jinja2.ext.with_'],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # look for templates explicitly under squad.api so that Django REST
        # Framework finds rest_framework/api.html in there
        'DIRS': [os.path.join(BASE_DIR, 'squad/frontend/templates/django/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'squad.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
    }
}
database_config = os.getenv('DATABASE')
if database_config:
    db_from_env = dict(x.split('=') for x in database_config.split(':'))
    DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en'

__local_languages__ = set([LANGUAGE_CODE])
for f in glob('%s/squad/*/locale/*/LC_MESSAGES' % BASE_DIR):
    lang = f.split('/')[-2]
    __local_languages__.add(lang.replace('_', '-').lower())

LANGUAGES = [e for e in global_settings.LANGUAGES if e[0] in __local_languages__]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# staticfile courtesy of whitenoise
# http://whitenoise.evans.io/en/stable/django.html
STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('SQUAD_STATIC_DIR', os.path.join(DATA_DIR, 'static'))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Always use IPython for shell_plus
SHELL_PLUS = "ipython"

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
SQUAD_LOGIN_MESSAGE = os.getenv("SQUAD_LOGIN_MESSAGE")

SITE_NAME = os.getenv('SQUAD_SITE_NAME', 'SQUAD')

SQUAD_ADMINS = os.getenv('SQUAD_ADMINS')
ADMINS = SQUAD_ADMINS and [parseaddr(s.strip()) for s in SQUAD_ADMINS.split(',')] or []

logging_handlers = ['console']
if not DEBUG and ADMINS:
    logging_handlers += ['mail_admins']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'myformatter': {
            'class': 'logging.Formatter',
            "format": "[%(asctime)s] [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S %z",
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'myformatter',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': logging_handlers,
            'propagate': False,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        '': {
            'handlers': logging_handlers,
            'propagate': False,
            'level': os.getenv('SQUAD_LOG_LEVEL', DEBUG and 'DEBUG' or 'INFO'),
        }
    }
}

HOSTNAME = os.getenv("SQUAD_HOSTNAME")
if not HOSTNAME:
    import socket
    HOSTNAME = socket.getfqdn()

BASE_URL = os.getenv('SQUAD_BASE_URL')
if not BASE_URL:
    BASE_URL = 'https://%s' % HOSTNAME

EMAIL_FROM = os.getenv('SQUAD_EMAIL_FROM')
if not EMAIL_FROM:
    EMAIL_FROM = 'noreply@%s' % HOSTNAME
SERVER_EMAIL = EMAIL_FROM

EMAIL_HOST = os.getenv("SQUAD_EMAIL_HOST", "localhost")

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Celery settings
CELERY_BROKER_URL = os.getenv('SQUAD_CELERY_BROKER_URL')
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 5,
}
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_BEAT_SCHEDULE_FILENAME = os.path.join(DATA_DIR, 'celerybeat-schedule')
CELERY_BEAT_SCHEDULE = {
    'poll-every-hour': {
        'task': 'squad.ci.tasks.poll',
        'schedule': crontab(hour='*/1', minute=17),
    },
    'cleanup': {
        'task': 'squad.core.tasks.cleanup_old_builds',
        'schedule': crontab(hour='3', minute=41),
    },
    'report_cleanup': {
        'task': 'squad.core.tasks.remove_delayed_reports',
        'schedule': crontab(hour='7', minute=21),
    }
}
CELERY_TASK_ROUTES = {
    'squad.core.tasks.prepare_report': {'queue': 'core_reporting'},
    'squad.core.tasks.postprocess_test_run': {'queue': 'core_postprocess'},
    'squad.core.tasks.cleanup_old_builds': {'queue': 'core_quick'},
    'squad.core.tasks.remove_delayed_reports': {'queue': 'core_quick'},
    'squad.core.tasks.cleanup_build': {'queue': 'core_quick'},
    'squad.core.tasks.maybe_notify_project_status': {'queue': 'core_notification'},
    'squad.core.tasks.notify_project_status': {'queue': 'core_notification'},
    'squad.core.tasks.notification_timeout': {'queue': 'core_notification'},
    'squad.core.tasks.notify_patch_build_created': {'queue': 'core_notification'},
    'squad.core.tasks.notify_patch_build_finished': {'queue': 'core_notification'},
    'squad.core.tasks.notify_delayed_report_callback': {'queue': 'core_notification'},
    'squad.core.tasks.notify_delayed_report_email': {'queue': 'core_notification'},
    'squad.ci.tasks.poll': {'queue': 'ci_poll'},
    'squad.ci.tasks.fetch': {'queue': 'ci_fetch'},
    'squad.ci.tasks.submit': {'queue': 'ci_quick'},
    'squad.ci.tasks.send_testjob_resubmit_admin_email': {'queue': 'ci_quick'},
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
        'squad.api.utils.DisabledHTMLFilterBackend',
    ),
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'squad.api.utils.BrowsableAPIRendererWithoutForms',
    ),
}

# CORS setup
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ['GET', 'HEAD']

CRISPY_TEMPLATE_PACK = 'bootstrap3'

try:
    from squad.local_settings import *  # noqa: F401,F403
except ImportError:
    pass

exec(open(os.getenv('SQUAD_EXTRA_SETTINGS', '/dev/null')).read())
