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
            cache = caches[getattr(settings, 'TOS_CACHE_NAME', 'default')]

            TermsOfService = self.get_model('TermsOfService')

            @receiver(pre_save, sender=TermsOfService, dispatch_uid='invalidate_cached_agreements')
            def invalidate_cached_agreements(TermsOfService, instance, **kwargs):
                if kwargs.get('raw', False):
                    return

                # Set the key version to 0 if it doesn't exist and leave it
                # alone if it does
                cache.add('django:tos:key_version', 0)

                # This key will be used to version the rest of the TOS keys
                # Incrementing it will effectively invalidate all previous keys
                cache.incr('django:tos:key_version')

            # Create the TOS key version immediately
            invalidate_cached_agreements(TermsOfService, None)
