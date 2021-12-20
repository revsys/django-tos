from django.urls import re_path

from tos.views import check_tos, TosView


urlpatterns = [
    # Terms of Service conform
    re_path(r'^confirm/$', check_tos, name='tos_check_tos'),

    # Terms of service simple display
    re_path(r'^$', TosView.as_view(), name='tos'),
]
