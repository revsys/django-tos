from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from tos.admin import TermsOfServiceAdmin

# Admin translation for django-plans
from tos.models import TermsOfService


class TranslatedTermsOfServiceAdmin(TermsOfServiceAdmin, TranslationAdmin):
    pass

admin.site.unregister(TermsOfService)
admin.site.register(TermsOfService, TranslatedTermsOfServiceAdmin)
