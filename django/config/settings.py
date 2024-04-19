import os
from datetime import timedelta
from pathlib import Path
from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

#WEBSITE_URL = env.str('WEBSITE_URL')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", )


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=180),
    'ROTATE_REFRESH_TOKENS': False,
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'drf_spectacular', # open api schema
    'treebeard',  # directories tree
    'corsheaders',
    'rest_framework',
    # https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html
    'rest_framework_simplejwt',  # Simple JWT
    'django_filters',  # for searching
    # 'django_cleanup',
    # 'debug_toolbar',

    # Local
    "accounts.apps.AccountsConfig",
    'blog.apps.BlogConfig',
    'blog.services'
]

AUTH_USER_MODEL = 'accounts.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # add
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'allauth.account.middleware.AccountMiddleware',  # add
# for debug-toolbar
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
#     'django.contrib.sites.middleware.CurrentSiteMiddleware',

]
# AUTHENTICATION_BACKENDS = [
#     "django.contrib.auth.backends.ModelBackend",
#     "allauth.account.auth_backends.AuthenticationBackend",  # new
# ]

SITE_ID = 1

ACCOUNT_EMAIL_VERIFICATION = "none"  # new

LOGIN_REDIRECT_URL = "/"  # new

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',  # auth
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
# ASGI_APPLICATION = 'config.asgi.application'
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': env.dj_db_url("DATABASE_URL")
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'
# LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # work in localserver

# STATIC_ROOT = os.path.join(BASE_DIR, "static")  # work with gunicorn
# for gunicorn
#MEDIA_URL = 'http://localhost:8008/media/'
# for dev
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#  https://docs.djangoproject.com/en/5.0/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        # "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        'LOCATION': os.path.join(BASE_DIR, 'cache'),

    }

}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    "DATETIME_FORMAT": "%d.%m.%Y",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 6,

    # For return only JSON
    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    # ],
    # 'DEFAULT_PARSER_CLASSES': (
    #     'rest_framework.parsers.JSONParser',
    #     'rest_framework.parsers.FormParser',
    #     'rest_framework.parsers.MultiPartParser',
    # ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'my-app-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'my-refresh-token',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Weare API',
    'DESCRIPTION': 'Django rest framework api for upload images and videos. User registration and verify email.',
    'VERSION': '0.0.1',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}


# for registration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('DJANGO_EMAIL_HOST', default='smtp.gmail.com')
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_HOST_USER = env.str('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('DJANGO_EMAIL_HOST_PASSWORD')
# EMAIL_TO = env.str('DJANGO_EMAIL_TO')

# https://stackoverflow.com/questions/76093862/dj-rest-auth-registration-return-http-204-no-content
# REST_AUTH = {
#     'SESSION_LOGIN': False
# }

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"


# for debug-toolbar
# for debug toolbar in docker
# https://ranjanmp.medium.com/
# django-debug-toolbar-not-showing-up-when-using-docker-django-docker-e79585813bc6
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1']
