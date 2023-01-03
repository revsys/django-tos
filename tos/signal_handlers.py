from django.conf import settings
from django.core.cache import caches


# Force the user to create a separate cache
cache = caches[getattr(settings, 'TOS_CACHE_NAME', 'default')]


def invalidate_cached_agreements(sender, **kwargs):
    if kwargs.get('raw', False):
        return

    # Set the key version to 0 if it doesn't exist and leave it
    # alone if it does
    cache.add('django:tos:key_version', 0)

    # This key will be used to version the rest of the TOS keys
    # Incrementing it will effectively invalidate all previous keys
    cache.incr('django:tos:key_version')
