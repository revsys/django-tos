import django
from django.conf import settings


def get_fk_user_model():
    if django.VERSION >= (1, 5):
        return settings.AUTH_USER_MODEL
    else:
        from django.contrib.auth.models import User
        return User


def get_runtime_user_model():
    if django.VERSION >= (1, 5):
        from django.contrib.auth import get_user_model
        return get_user_model()
    else:
        from django.contrib.auth.models import User
        return User
