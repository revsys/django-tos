from django.urls import include, re_path
from django.views.generic import TemplateView

from tos import views


urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),

    re_path(r'^login/$', views.login, {}, 'login'),
    re_path(r'^tos/', include('tos.urls')),
]
