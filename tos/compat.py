import django
from django.conf import settings


def get_fk_user_model():
    if django.VERSION >= (1, 5):
        return settings.AUTH_USER_MODEL
    return django.contrib.auth.models.User


def get_runtime_user_model():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model
        return get_user_model()
    return django.contrib.auth.models.User


def get_request_site():
    if django.VERSION >= (1, 9):
        return django.contrib.sites.requests.RequestSite
    return django.contrib.sites.models.RequestSite


def get_library():
    if django.VERSION >= (1, 9):
        return django.template.library.Library
    return django.template.base.Library


if django.VERSION < (1, 5):
    from django.templatetags.future import url
else:
    from django.template.defaulttags import url
