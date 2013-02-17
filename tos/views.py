from django.views.generic import TemplateView
import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site, RequestSite
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext_lazy as _

from tos.models import has_user_agreed_latest_tos, TermsOfService, UserAgreement

class TosView(TemplateView):
    template_name = "tos/tos.html"

    def get_context_data(self, **kwargs):
        context = super(TosView, self).get_context_data(**kwargs)
        context['tos'] = TermsOfService.objects.get_current_tos()
        return context


def _redirect_to(redirect_to):
    """ Moved redirect_to logic here to avoid duplication in views"""
    
    # Light security check -- make sure redirect_to isn't garbage.
    if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL

    # Heavier security check -- redirects to http://example.com should 
    # not be allowed, but things like /view/?param=http://example.com 
    # should be allowed. This regex checks if there is a '//' *before* a
    # question mark.
    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
            redirect_to = settings.LOGIN_REDIRECT_URL
    return redirect_to

@csrf_protect
@never_cache
def check_tos(request, template_name='tos/tos_check.html',
    redirect_field_name=REDIRECT_FIELD_NAME,):

    redirect_to = _redirect_to(request.REQUEST.get(redirect_field_name, ''))
    tos = TermsOfService.objects.get_current_tos()
    if request.method=="POST":
        if request.POST.get("accept", "") == "accept":
            user = request.session['tos_user']
            
            # Save the user agreement to the new TOS
            UserAgreement.objects.create(terms_of_service=tos, user=user)
            
            # Log the user in            
            auth_login(request, user)

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
        else:
            messages.error(request, _(u"You cannot login without agreeing to the terms of this site."))


    return render_to_response(template_name, {
        'tos':tos,

        redirect_field_name: redirect_to,
    }, context_instance=RequestContext(request))
    
    
        
@csrf_protect
@never_cache        
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():

            redirect_to = _redirect_to(redirect_to)
                    
            # Okay, security checks complete. Check to see if user agrees to terms
            user = form.get_user()
            if has_user_agreed_latest_tos(user):

                # Log the user in.
                auth_login(request, user)

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return HttpResponseRedirect(redirect_to)
                
            else:
                # user has not yet agreed to latest tos
                # force them to accept or refuse
                
                request.session['tos_user'] = user
                
                
                return render_to_response('tos/tos_check.html', {
                    redirect_field_name: redirect_to,
                    'tos': TermsOfService.objects.get_current_tos()
                }, context_instance=RequestContext(request))                

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))

