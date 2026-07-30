"""Django settings used when running the django-tos test suite via pytest."""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "tos",
    "tos.tests",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tos.tests.test_urls"
LOGIN_URL = "/login/"
SITE_ID = 1

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "tos": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

SECRET_KEY = "7v%d@z##e=8z5#oc=cc-o%!cka5ibyy7#9r!#2fyiwn7ki020y"
TOS_CACHE_NAME = "tos"

USE_TZ = True
