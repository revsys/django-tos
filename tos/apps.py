from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import pre_save

from .signal_handlers import invalidate_cached_agreements


class TOSConfig(AppConfig):
    name = 'tos'
    verbose_name = 'Terms Of Service'

    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        MIDDLEWARES = getattr(settings, 'MIDDLEWARE', [])
        if 'tos.middleware.UserAgreementMiddleware' in MIDDLEWARES:  # pragma: no cover
            TermsOfService = self.get_model('TermsOfService')

            pre_save.connect(invalidate_cached_agreements,
                             sender=TermsOfService,
                             dispatch_uid='invalidate_cached_agreements')

            # Create the TOS key version immediately
            invalidate_cached_agreements(TermsOfService)
