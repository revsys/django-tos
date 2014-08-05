from django.conf.urls import patterns, include

urlpatterns = patterns('',
        (r'^login/$', 'tos.views.login', {}, 'login',),
        (r'^tos/', include('tos.urls')),
    )
