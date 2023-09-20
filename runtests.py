#!/usr/bin/env python
import logging
import sys

import django

from django.conf import settings
from django.core.management import execute_from_command_line


if not settings.configured:
    django_settings = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        'DEFAULT_AUTO_FIELD': 'django.db.models.AutoField',
        'INSTALLED_APPS': [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.sites',
            'tos',
            'tos.tests'
        ],
        'TEMPLATES': [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
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
        ],
        'ROOT_URLCONF': 'tos.tests.test_urls',
        'LOGIN_URL': '/login/',
        'SITE_ID': 1,
        'CACHES': {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            },
            'tos': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        'SECRET_KEY': '7v%d@z##e=8z5#oc=cc-o%!cka5ibyy7#9r!#2fyiwn7ki020y',
        'TOS_CACHE_NAME': 'tos'
    }

    django_settings['MIDDLEWARE'] = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    settings.configure(**django_settings)


logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
)
logging.disable(logging.CRITICAL)


def runtests():
    argv = sys.argv[:1] + ['test', 'tos']
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
