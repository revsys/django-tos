from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import pre_save

from .signal_handlers import invalidate_cached_agreements

from .compat import get_middleware_settings_key


middleware_settings_key = get_middleware_settings_key()
MIDDLEWARES = getattr(settings, middleware_settings_key, [])


class TOSConfig(AppConfig):
    name = 'tos'
    verbose_name = 'Terms Of Service'

    def ready(self):
        if 'tos.middleware.UserAgreementMiddleware' in MIDDLEWARES:
            TermsOfService = self.get_model('TermsOfService')

            pre_save.connect(invalidate_cached_agreements,
                             sender=TermsOfService,
                             dispatch_uid='invalidate_cached_agreements')

            # Create the TOS key version immediately
            invalidate_cached_agreements(TermsOfService, None)
