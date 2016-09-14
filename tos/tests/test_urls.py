from django.conf.urls import include, url

from tos.compat import patterns
from tos import views

urlpatterns = patterns('',
    url(r'^login/$', views.login, {}, 'login'),
    url(r'^tos/', include('tos.urls')),
)
