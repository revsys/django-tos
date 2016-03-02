from django.contrib import admin

from tos.models import TermsOfService, UserAgreement


class TermsOfServiceAdmin(admin.ModelAdmin):
    model = TermsOfService

admin.site.register(TermsOfService, TermsOfServiceAdmin)


class UserAgreementAdmin(admin.ModelAdmin):
    model = UserAgreement

admin.site.register(UserAgreement, UserAgreementAdmin)
