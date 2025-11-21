from typing import TYPE_CHECKING

from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


def get_tos_cache():
    return caches[getattr(settings, 'TOS_CACHE_NAME', 'default')]


cache = get_tos_cache()


def initialize_cache_version():
    if not cache.get('django:tos:key_version', False):
        # The function is a signal handler, so it needs a sender argument, but
        # it doesn't actually use it at all, so it can be None
        invalidate_cached_agreements(sender=None)


def invalidate_cached_agreements(sender, **kwargs):
    # Set the key version to 0 if it doesn't exist and leave it
    # alone if it does
    cache.add('django:tos:key_version', 0)

    # This key will be used to version the rest of the TOS keys
    # Incrementing it will effectively invalidate all previous keys
    cache.incr('django:tos:key_version')


def add_staff_users_to_tos_cache(*args, **kwargs):
    if kwargs.get('raw', False):
        return

    # Get the cache prefix
    key_version = cache.get('django:tos:key_version')

    # Efficiently cache all of the users who are allowed to skip the TOS
    # agreement check
    cache.set_many({
        f'django:tos:skip_tos_check:{staff_user.id}': True
        for staff_user in get_user_model().objects.filter(
            Q(is_staff=True) | Q(is_superuser=True))
    }, version=key_version)


def set_staff_in_cache_for_tos(*, instance: 'AbstractUser', **kwargs):
    if kwargs.get('raw', False):
        return

    # Get the cache prefix
    key_version = cache.get('django:tos:key_version')

    # If the user is staff allow them to skip the TOS agreement check
    if instance.is_staff or instance.is_superuser:
        cache.set(f'django:tos:skip_tos_check:{instance.id}', True, version=key_version)

    # But if they aren't make sure we invalidate them from the cache
    elif cache.get(f'django:tos:skip_tos_check:{instance.id}', False):
        cache.delete(f'django:tos:skip_tos_check:{instance.id}', version=key_version)
