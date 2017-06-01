from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, SESSION_KEY as session_key
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import deprecation
from django.utils.cache import add_never_cache_headers

from .compat import get_cache
from .models import UserAgreement

cache = get_cache(getattr(settings, 'TOS_CACHE_NAME', 'default'))
tos_check_url = reverse('tos_check_tos')


class UserAgreementMiddleware(deprecation.MiddlewareMixin if DJANGO_VERSION >= (1, 10, 0) else object):
    """
    Some middleware to check if users have agreed to the latest TOS
    """
    def process_request(self, request):
        # Don't get in the way of any mutating requests
        if request.method != 'GET':
            return None

        # Ignore ajax requests
        if request.is_ajax():
            return None

        # Don't redirect users when they're trying to get to the confirm page
        if request.path_info == tos_check_url:
            return None

        # If the user doesn't have a user ID, ignore them - they're anonymous
        if not request.session.get(session_key, None):
            return None

        # Grab the user ID from the session so we avoid hitting the database
        # for the user object.
        # NOTE: We use the user ID because it's not user-settable and it won't
        #       ever change (usernames and email addresses can change)
        user_id = request.session['_auth_user_id']
        user_auth_backend = request.session['_auth_user_backend']

        # Get the cache prefix
        key_version = cache.get('django:tos:key_version')

        # Skip if the user is allowed to skip - for instance, if the user is an
        # admin or a staff member
        if cache.get('django:tos:skip_tos_check:{0}'.format(str(user_id)), False, version=key_version):
            return None

        # Ping the cache for the user agreement
        user_agreed = cache.get('django:tos:agreed:{0}'.format(str(user_id)), None, version=key_version)

        # If the cache is missing this user
        if user_agreed is None:
            # Grab the data from the database
            user_agreed = UserAgreement.objects.filter(
                user__id=user_id,
                terms_of_service__active=True).exists()

            # Set the value in the cache
            cache.set('django:tos:agreed:{0}'.format(user_id), user_agreed, version=key_version)

        if not user_agreed:
            # Confirm view uses these session keys. Non-middleware flow sets them in login view,
            # so we need to set them here.
            request.session['tos_user'] = user_id
            request.session['tos_backend'] = user_auth_backend

            response = HttpResponseRedirect('{0}?{1}={2}'.format(
                tos_check_url,
                REDIRECT_FIELD_NAME,
                request.path_info,
            ))
            add_never_cache_headers(response)
            return response

        return None
