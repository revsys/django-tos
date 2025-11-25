from django.conf import settings
from django.core.cache import caches

from tos.utils import invalidate_cached_agreements as invalidate_cached_agreements_func


def invalidate_cached_agreements(sender, **kwargs):
    if kwargs.get('raw', False):
        return

    invalidate_cached_agreements_func(sender)
