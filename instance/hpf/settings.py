# Django settings for the HPF project.

import platform, os, hashlib
virtualpath = lambda *pths: os.path.join('/Users/fish/Praxa/HPF', *pths)
hasher = lambda token: hashlib.sha256(token).hexdigest()

secret = "4ec705d96b2fc89fa946944881897a6e01269b1ffe1a7776e6f676aeeedd1871"
if os.path.isfile(virtualpath('.password')):
    with open(virtualpath('.password'), 'rb') as passfile:
        password = passfile.read()
        secret = hasher(password)

BASE_HOSTNAME = platform.node().lower()
DEPLOYED = not BASE_HOSTNAME.endswith('.local')

DEBUG = not DEPLOYED
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS
SECRET_KEY = secret

if DEPLOYED:
    ALLOWED_HOSTS = ['*']

pooled_database = {
    'NAME': 'hpf',
    'ENGINE': 'django_postgrespool',
    'USER': 'hpf',
    'PASSWORD': password,
    'OPTIONS': dict(autocommit=True),
}

default_database = {
    'NAME': 'hpf',
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'USER': 'hpf',
    'PASSWORD': password,
    'OPTIONS': dict(autocommit=True),
}

if DEPLOYED:
    default_database.update({
        'HOST': 'localhost',
        'PORT': 5432 })

DATABASES = { 'default': default_database }
SOUTH_DATABASE_ADAPTERS = { 'default': 'south.db.postgresql_psycopg2' }

DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_size': 20,
    'recycle': 300
}

memcache = {
    'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
    'LOCATION': virtualpath('var', 'run', 'memcached.sock'),
    'KEY_PREFIX': 'hpf' }

localmemory = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'hpf' }

CACHES = {
    'default': DEPLOYED and memcache or localmemory
}

if DEPLOYED:
    CACHE_MIDDLEWARE_SECONDS = 60
    CACHE_MIDDLEWARE_KEY_PREFIX = "hpf_cache"
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1 # must be this (verbatim) for allauth
USE_I18N = False
USE_L10N = False
USE_TZ = False

MEDIA_ROOT = virtualpath('var', 'web', 'face')
MEDIA_URL = '/face/'
TEMPLATE_DIRS = ()
STATIC_ROOT = virtualpath('var', 'web', 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = DEPLOYED and (
    # Caching is enabled.
    # N.B. The order of these matters, evidently
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
) or (
    # Caching is disabled.
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    #"django.core.context_processors.i18n", this is AMERICA
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    # ALL-AUTH ALL THE WAY DOWN
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

AUTHENTICATION_BACKENDS = (
    # Django auth backend for vanilla admin logins with usernames
    "django.contrib.auth.backends.ModelBackend",
    # All-auth backend/backends
    "allauth.account.auth_backends.AuthenticationBackend",
)

ROOT_URLCONF = 'hpf.urls'
WSGI_APPLICATION = 'hpf.wsgi.application'
AUTH_USER_MODEL = 'hamptons.Hamptonian'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.twitter',
    
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django_extensions',
    
    'south',
    'gunicorn',
    'imagekit',
    
    'IGA',
    'hamptons',
    'sandpiper',
)


LOGIN_REDIRECT_URL = "/hamptons/mobile/index.html"
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_USER_DISPLAY = lambda user: "@%s" % user.username
ACCOUNT_USERNAME_MIN_LENGTH = 2
ACCOUNT_USERNAME_BLACKLIST = ['fish']
SOCIALACCOUNT_QUERY_EMAIL = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'elasticsearch.trace': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
