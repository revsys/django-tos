from django.conf.urls import url

from tos.compat import patterns
from tos.views import check_tos, TosView


urlpatterns = patterns('',
    # Terms of Service conform
    url(r'^confirm/$', check_tos, name='tos_check_tos'),

    # Terms of service simple display
    url(r'^$', TosView.as_view(), name='tos'),
)
