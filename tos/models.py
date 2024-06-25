import warnings

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class NoActiveTermsOfService(ValidationError):
    pass


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class TermsOfServiceManager(models.Manager):
    def get_current_tos(self):
        try:
            return self.get(active=True)
        except self.model.DoesNotExist:
            if settings.DEBUG:
                warnings.warn("There is no active Terms-of-Service")
            else:
                raise NoActiveTermsOfService(
                    'Please create an active Terms-of-Service'
                )


class TermsOfService(BaseModel):
    active = models.BooleanField(
                default=False,
                verbose_name=_('active'),
                help_text=_(
                    'Only one terms of service is allowed to be active'
                )
    )
    content = models.TextField(verbose_name=_('content'), blank=True)
    objects = TermsOfServiceManager()

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = _('Terms of Service')
        verbose_name_plural = _('Terms of Service')

    def __str__(self):
        active = 'inactive'
        if self.active:
            active = 'active'
        return f'{self.created}: {active}'

    def save(self, *args, **kwargs):
        """ Ensure we're being saved properly """

        if self.active:
            TermsOfService.objects.exclude(id=self.id).update(active=False)

        else:
            if not TermsOfService.objects\
                    .exclude(id=self.id)\
                    .filter(active=True)\
                    .exists():
                if settings.DEBUG:
                    warnings.warn("There is no active Terms-of-Service")
                else:
                    raise NoActiveTermsOfService(
                        'One of the terms of service must be marked active'
                    )

        super().save(*args, **kwargs)


class UserAgreement(BaseModel):
    terms_of_service = models.ForeignKey(TermsOfService, related_name='terms', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_agreement', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} agreed to TOS: {self.terms_of_service}'


def has_user_agreed_latest_tos(user):
    return UserAgreement.objects.filter(
        terms_of_service=TermsOfService.objects.get_current_tos(),
        user=user,
    ).exists()
