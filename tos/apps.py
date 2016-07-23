from django.apps import AppConfig
from django.conf import settings
from django.core.cache import caches
from django.db.models.signals import pre_save
from django.dispatch import receiver


MIDDLEWARES = getattr(settings, 'MIDDLEWARE_CLASSES', [])


class TOSConfig(AppConfig):
    name = 'tos'
    verbose_name = 'Terms Of Service'

    def ready(self):
        if 'tos.middleware.UserAgreementMiddleware' in MIDDLEWARES:
            # Force the user to create a separate cache
            cache = caches[getattr(settings, 'TOS_CACHE_NAME')]

            TermsOfService = self.get_model('TermsOfService')

            @receiver(pre_save, sender=TermsOfService, dispatch_uid='invalidate_cached_agreements')
            def invalidate_cached_agreements(TermsOfService, instance, **kwargs):
                if kwargs.get('raw', False):
                    return

                # Efficiently clear all keys from the cache
                cache.clear()
