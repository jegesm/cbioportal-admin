"""
Django settings for cbioportal project.
"""
import os
from os import path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

SESSION_COOKIE_NAME = "cbioportal_sessionid"


DEBUG = True

PREFIX = os.getenv('PREFIX', 'cbioportal')
DOMAIN = os.getenv('DOMAIN', 'localhost')
CBIOPORTAL_NAME = os.getenv('CBIOPORTAL_NAME', 'cbioportal')

tLDAP_DOMAIN = os.getenv('LDAP_DOMAIN', 'dc=%s' % ',dc='.join(DOMAIN.split('.')))
LDAP_ADMIN = os.getenv('LDAP_ADMIN', 'admin')

ALLOWED_HOSTS = (
            DOMAIN,
                '%s-nginx' % PREFIX,
    'localhost',
    'kooplex-fiek.elte.hu',
                )

#INSTALLED_APPS = (
#            'django.contrib.admin',
#            'django.contrib.auth',
#            'django.contrib.contenttypes',
##            'django.contrib.sites',
#            'django.contrib.sessions',
#            'django.contrib.messages',
#            'django.contrib.staticfiles',
#            'social_django',
#            'django_tables2',
##            'bootstrap3',
##            'hub',
#)


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cbioportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'cbioportal/templates') ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
#                'cbioportal.lib.context_processors.user',
#                'cbioportal.lib.context_processors.table',
#                'cbioportal.lib.context_processors.manual',
            ],
        },
    },
]

WSGI_APPLICATION = 'cbioportal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB', 'cbioportal'),
        'USER': os.getenv('DB_USER', PREFIX),
        'PASSWORD': os.getenv('DB_PW'),
        'HOST': '%s-%s-mysql' % (PREFIX, CBIOPORTAL_NAME),
        'PORT': '3306',
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIME_ZONE', 'Europe/Budapest')

USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


#LOGIN_REDIRECT_URL = 'indexpage'
LOGOUT_URL = '' #'https://%s.elte.hu/consent/auth/logout' % PREFIX

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
       'verbose': {
            'format': '%(levelname)s[%(asctime)s]\t%(module)s:%(funcName)s:%(lineno)s -- %(message)s'
        },
    },
    'handlers': {
        'dfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['dfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
   }
}

DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

SETTINGS = {
#    'base_url': 'https://%s/cbioprtal-admin/' % DOMAIN,
    'base_url': 'https://%s/' % DOMAIN,
    'ldap': {
        'host': '%s-%s-ldap' % (PREFIX, CBIOPORTAL_NAME),
        'port': int(os.getenv('LDAP_PORT', 389)),
        'bind_dn': 'cn=%s,%s' % (LDAP_ADMIN, tLDAP_DOMAIN),
        'base_dn': tLDAP_DOMAIN,
        'bind_username': LDAP_ADMIN,
        'bind_password': os.getenv('LDAP_PW'),
    },
    'user': {
        'min_userid': 10000,
        'pattern_passwordfile': '/tmp/pw.%(username)s',
        },
}

AUTHENTICATION_BACKENDS = (
    'cbioportal.idp.adminAuthBackend',
    'cbioportal.idp.localAuthBackend',
)

#KOOPLEX_OUTER_HOST = 'kooplex.vo.elte.hu'
#KOOPLEX_INTERNAL_HOST = '192.168.122.12'
#KOOPLEX_INTERNAL_HOSTNAME = '192.168.122.12'
#KOOPLEX_OUTER_PORT = ''
#
#PROTOCOL = "https"
#KOOPLEX_BASE_URL = PROTOCOL + '://' + KOOPLEX_OUTER_HOST
#KOOPLEX_HUB_PREFIX = 'hub'



#STATIC_ROOT = path.join(PROJECT_ROOT, 'static').replace('\\', '/')


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'threadlocals.middleware.ThreadLocalMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
CORS_ORIGIN_ALLOW_ALL = True



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cbioportal.hub.apps.HubConfig',
    'cbioportal.hub.templatetags',
    'django.contrib.admin',
    'django.contrib.admindocs',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}

# Paste into each file maybe ?
# import logging
# logger = logging.getLogger(__name__)


#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'formatters': {
#       'verbose': {
#            'format': '%(levelname)s -- [%(asctime)s] %(module)s:%(lineno)s - %(funcName)s -  %(message)s'
#        },
#        'tooverbose': {
#            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#        },
#        'simple': {
#            'format': '%(levelname)s %(message)s'
#        },
#    },
#    'filters': {
#        'require_debug_false': {
#            '()': 'django.utils.log.RequireDebugFalse'
#        }
#    },
#    'handlers': {
#        'mail_admins': {
#            'level': 'ERROR',
#            'filters': ['require_debug_false'],
#            'class': 'django.utils.log.AdminEmailHandler'
#        },
#        'dfile': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': '/tmp/debug-hub.log',
#            'formatter': 'verbose',
#        },
#        'ifile': {
#            'level': 'INFO',
#            'class': 'logging.FileHandler',
#            'filename': '/tmp/info-hub.log',
#            'formatter': 'verbose',
#        },
#        'wfile': {
#            'level': 'WARNING',
#            'class': 'logging.FileHandler',
#            'filename': '/tmp/warning-hub.log',
#            'formatter': 'verbose',
#        },
#        'efile': {
#            'level': 'ERROR',
#            'class': 'logging.FileHandler',
#            'filename': '/tmp/error-hub.log',
#            'formatter': 'verbose',
#        },
#        'file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': '/tmp/django.log',
#        },
#
#    },
#    'loggers': {
#        'django.request': {
#            'handlers': ['mail_admins'],
#            'level': 'ERROR',
#            'propagate': True,
#        },
#        'cbioportal': {
#            'handlers': ['dfile', 'ifile', 'wfile', 'efile'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#        'django': {
#            'handlers': ['file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#
#   }
#}
#
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
