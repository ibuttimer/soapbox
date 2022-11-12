#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

"""
Django settings for soapbox project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

import environ
from django.contrib.messages import constants as messages

from .constants import (
    BASE_APP_NAME, USER_APP_NAME, CATEGORIES_APP_NAME, OPINIONS_APP_NAME,
    MIN_PASSWORD_LEN
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    DEVELOPMENT=(bool, False),
    TEST=(bool, False)
)
# Take environment variables from .env file
os.environ.setdefault('ENV_FILE', '.env')
environ.Env.read_env(
    os.path.join(BASE_DIR, env('ENV_FILE'))
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
DEVELOPMENT = env('DEVELOPMENT')

# https://docs.djangoproject.com/en/4.1/ref/clickjacking/
# required for Summernote editor
X_FRAME_OPTIONS = 'SAMEORIGIN'
SUMMERNOTE_THEME = 'bs4'    # TODO bs5 not working at the moment
# https://github.com/summernote/django-summernote#options
SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode, default
    'iframe': True,

    # You can put custom Summernote settings
    'summernote': {
        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '240',

        # Use proper language setting automatically (default)
        'lang': None,

        # Toolbar customization
        # https://summernote.org/deep-dive/#custom-toolbar-popover
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
    },
    # Require users to be authenticated for uploading attachments.
    'attachment_require_authentication': True,

    # Lazy initialization
    # If you want to initialize summernote at the bottom of page,
    # set this as True and call `initSummernote()` on your page.
    'lazy': False,
    # TODO need to figure out initSummernote for admin site to enable this
}

if env('DEVELOPMENT'):
    ALLOWED_HOSTS = ['testserver'] \
        if env('TEST') else ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = [env('HEROKU_HOSTNAME')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',

    # The following apps are required by 'allauth':
    #   django.contrib.auth, django.contrib.messages
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',

    # https://pypi.org/project/dj3-cloudinary-storage/
    # If using for static and/or media files, make sure that cloudinary_storage
    # is before django.contrib.staticfiles
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'django_summernote',
    BASE_APP_NAME,
    CATEGORIES_APP_NAME,
    OPINIONS_APP_NAME,
    USER_APP_NAME,

    # needs to be after app with django template overrides
    'django.forms',
]

# To supply custom templates to django widgets:
# 1) Add 'django.forms' to INSTALLED_APPS; *after* the app with the overrides.
# 2) Add FORM_RENDERER = 'django.forms.renderers.TemplatesSetting' to
#    settings.py.
# Courtesy of https://stackoverflow.com/a/52184422/4054609
# https://docs.djangoproject.com/en/4.1/ref/forms/renderers/#django.forms.renderers.TemplatesSetting
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soapbox.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # `allauth` needs this from django
                'django.template.context_processors.request',
                # soapbox context processors
                'soapbox.context_processors.footer_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'soapbox.wsgi.application'

AUTH_USER_MODEL = 'user.User'

# 'allauth' site id
SITE_ID = int(env('SITE_ID'))
# 'allauth' provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        "APP": {
        },
        # These are provider-specific settings that can only be
        # listed here:
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        }
    },
    "twitter": {
        "APP": {
        },
    }

}
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    # Default setting, needed to login by username in Django admin,
    # regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# https://django-allauth.readthedocs.io/en/latest/forms.html
ACCOUNT_FORMS = {
    'signup': 'user.forms.UserSignupForm',
    'login': 'user.forms.UserLoginForm'
}

# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-MESSAGE_TAGS
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# Parse database connection url strings
# like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
    # read os.environ['DATABASE_URL'] and raises
    # ImproperlyConfigured exception if not found
    #
    # The db() method is an alias for db_url().
    'default': env.db(),

    # read os.environ['HEROKU_DATABASE_URL']
    'heroku': env.db_url(
        'HEROKU_DATABASE_URL',
        default='sqlite:////tmp/my-tmp-sqlite.db'
    ),

    # read os.environ['SQLITE_URL']
    'extra': env.db_url(
        'SQLITE_URL',
        default='sqlite:////tmp/my-tmp-sqlite.db'
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [{
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': MIN_PASSWORD_LEN,
        }
    }, {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# URL to use when referring to static files located in STATIC_ROOT
STATIC_URL = 'static/'
# https://docs.djangoproject.com/en/4.1/ref/settings/#staticfiles-storage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage' \
    if DEVELOPMENT else \
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-STATICFILES_DIRS
# Additional locations the staticfiles app will traverse for collectstatic
STATICFILES_DIRS = [
    # directories that will be found by staticfiles’s finders are by default,
    # are 'static/' app sub-directories and any directories included in
    # STATICFILES_DIRS
    os.path.join(BASE_DIR, 'static')
]
# absolute path to the directory where static files are collected for
# deployment
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-STATIC_ROOT
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-MEDIA_ROOT
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)


DEFAULT_FILE_STORAGE = \
    'django.core.files.storage.FileSystemStorage' \
    if DEVELOPMENT else \
    'cloudinary_storage.storage.MediaCloudinaryStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# url for blank avatar image
AVATAR_BLANK_URL = env('AVATAR_BLANK_URL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
