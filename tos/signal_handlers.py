from django.conf import settings

from .compat import get_cache

# Force the user to create a separate cache
cache = get_cache(getattr(settings, 'TOS_CACHE_NAME', 'default'))


def invalidate_cached_agreements(TermsOfService, instance, **kwargs):
    if kwargs.get('raw', False):
        return

    # Set the key version to 0 if it doesn't exist and leave it
    # alone if it does
    cache.add('django:tos:key_version', 0)

    # This key will be used to version the rest of the TOS keys
    # Incrementing it will effectively invalidate all previous keys
    cache.incr('django:tos:key_version')
