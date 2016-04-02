import django
from django.conf import settings


def get_fk_user_model():
    if django.VERSION >= (1, 5):
        return settings.AUTH_USER_MODEL
    from django.contrib.auth.models import User
    return User


def get_runtime_user_model():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model
        return get_user_model()
    from django.contrib.auth.models import User
    return User


def get_request_site():
    if django.VERSION >= (1, 9):
        from django.contrib.sites.requests import RequestSite
    else:
        from django.contrib.sites.models import RequestSite
    return RequestSite


def get_library():
    if django.VERSION >= (1, 9):
        from django.template.library import Library
    else:
        from django.template.base import Library
    return Library


if django.VERSION < (1, 5):
    from django.templatetags.future import url
else:
    from django.template.defaulttags import url
