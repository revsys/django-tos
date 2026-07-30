from modeltranslation.translator import TranslationOptions, translator

from tos.models import TermsOfService

# Translations for django-tos


class TermsOfServiceTranslationOptions(TranslationOptions):
    fields = ("content",)


translator.register(TermsOfService, TermsOfServiceTranslationOptions)
