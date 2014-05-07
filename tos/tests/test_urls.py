from django.conf.urls.defaults import * 

from tos.views import * 

urlpatterns = patterns('', 
        (r'^login/$', 'tos.views.login', {}, 'login',), 
        (r'^tos/', include('tos.urls')), 
    ) 
