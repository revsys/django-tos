from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import pre_save

from .signal_handlers import invalidate_cached_agreements
from .utils import initialize_cache_version


class TOSConfig(AppConfig):
    name = 'tos'
    verbose_name = 'Terms Of Service'

    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        MIDDLEWARES = getattr(settings, 'MIDDLEWARE', [])
        if 'tos.middleware.UserAgreementMiddleware' in MIDDLEWARES:  # pragma: no cover
            TermsOfService = self.get_model('TermsOfService')

            initialize_cache_version()

            pre_save.connect(invalidate_cached_agreements,
                             sender=TermsOfService,
                             dispatch_uid='invalidate_cached_agreements')
