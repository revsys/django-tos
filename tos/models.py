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
    def get_current_tos(self, slug="default"):
        try:
            return self.get(active=True, slug=slug)
        except self.model.DoesNotExist:
            if settings.DEBUG:
                warnings.warn("There is no active Terms-of-Service")
            else:
                raise NoActiveTermsOfService("Please create an active Terms-of-Service")

    def get_active(self):
        """Experimental: every active Terms of Service, one per ``slug``.

        With the default single-document setup this is just the one active
        Terms of Service; when several ``slug`` values are in use it returns the
        active document for each.
        """
        return self.filter(active=True)


class TermsOfService(BaseModel):
    active = models.BooleanField(
        default=False,
        verbose_name=_("active"),
        help_text=_("Only one terms of service is allowed to be active per slug"),
    )
    content = models.TextField(verbose_name=_("content"), blank=True)
    slug = models.SlugField(
        default="default",
        verbose_name=_("slug"),
        help_text=_(
            "Experimental: identifies the kind of agreement (e.g. 'default', 'privacy'). "
            "One active Terms of Service is allowed per slug, so a site can require "
            "agreement to several documents. Existing installs keep a single 'default' "
            "document and are unaffected."
        ),
    )
    objects = TermsOfServiceManager()

    class Meta:
        get_latest_by = "created"
        ordering = ("-created",)
        verbose_name = _("Terms of Service")
        verbose_name_plural = _("Terms of Service")

    def __str__(self):
        return f"{self.created}: {'active' if self.active else 'inactive'}"

    def save(self, *args, **kwargs):
        """Ensure we're being saved properly"""

        # The active/one-must-be-active invariant is enforced per ``slug`` so
        # that activating, say, a "privacy" document does not deactivate the
        # active "default" one.
        if self.active:
            TermsOfService.objects.exclude(id=self.id).filter(slug=self.slug).update(active=False)

        else:
            if not TermsOfService.objects.exclude(id=self.id).filter(active=True, slug=self.slug).exists():
                if settings.DEBUG:
                    warnings.warn("There is no active Terms-of-Service")
                else:
                    raise NoActiveTermsOfService("One of the terms of service must be marked active")

        super().save(*args, **kwargs)


class UserAgreement(BaseModel):
    terms_of_service = models.ForeignKey(TermsOfService, related_name="terms", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_agreement", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} agreed to TOS: {self.terms_of_service}"


def has_user_agreed_latest_tos(user):
    """Has ``user`` agreed to every active Terms of Service?

    With a single active document this is the classic "did the user agree to the
    current TOS" check. Experimental: when several ``slug`` values are active the
    user must have agreed to all of them.
    """
    active = TermsOfService.objects.filter(active=True)
    if not active.exists():
        # Preserve the "no active TOS" signal (DEBUG-gated warn or raise).
        TermsOfService.objects.get_current_tos()
        return False
    return not active.exclude(terms__user=user).exists()
