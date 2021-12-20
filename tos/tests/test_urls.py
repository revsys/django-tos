from django.conf.urls import include, url
from django.views.generic import TemplateView

from tos import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),

    url(r'^login/$', views.login, {}, 'login'),
    url(r'^tos/', include('tos.urls')),
]
