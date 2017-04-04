from django.conf.urls import include, url
from django.views.generic import TemplateView

from tos.compat import patterns
from tos import views

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),

    url(r'^login/$', views.login, {}, 'login'),
    url(r'^tos/', include('tos.urls')),
)
