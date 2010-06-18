from django.conf.urls.defaults import * 
from django.views.generic.simple import direct_to_template

from tos.models import TermsOfService
from tos.views import check_tos

urlpatterns = patterns('',
        # Terms of Service conform 
        url(
            regex   = '^confirm/$',
            view    = check_tos,
            name    = 'tos_check_tos',
        ),
        
        # Terms of service simple display 
        url(
            regex   = '^$',
            view    = direct_to_template,
            kwargs  = {'template': 'tos/tos.html',
                        'extra_context':{
                            'tos':TermsOfService.objects.get_current_tos()
                            },          
                        },
            name    = 'tos',
        ),
    )