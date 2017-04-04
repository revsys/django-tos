#!/usr/bin/env python
import sys

import django

from django.conf import settings
from django.core.management import execute_from_command_line


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.sites',
            'tos',
            'tos.tests'
        ],
        MIDDLEWARE_CLASSES=[
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        TEMPLATES=[
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
        ROOT_URLCONF='tos.tests.test_urls',
        LOGIN_URL='/login/',
        SITE_ID='1',
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            },
            'tos': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        TOS_CACHE_NAME = 'tos' 
    )


import logging
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
