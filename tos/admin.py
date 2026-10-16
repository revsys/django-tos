from django.contrib import admin

from tos.models import TermsOfService, UserAgreement


class TermsOfServiceAdmin(admin.ModelAdmin):
    model = TermsOfService
    list_display = ("slug", "created", "active")
    list_filter = ("slug", "active")


admin.site.register(TermsOfService, TermsOfServiceAdmin)


class UserAgreementAdmin(admin.ModelAdmin):
    model = UserAgreement


admin.site.register(UserAgreement, UserAgreementAdmin)
