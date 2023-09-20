from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.auth import SESSION_KEY as session_key
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.cache import caches
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.cache import add_never_cache_headers
from django.utils.deprecation import MiddlewareMixin

from .models import UserAgreement


cache = caches[getattr(settings, 'TOS_CACHE_NAME', 'default')]
tos_check_url = reverse_lazy('tos_check_tos')


class UserAgreementMiddleware(MiddlewareMixin):
    """
    Some middleware to check if users have agreed to the latest TOS
    """

    def __init__(self, get_response = None):
        if DJANGO_VERSION < (4,0):
            self.get_response = get_response
        else:
            if get_response is None:
                raise TypeError('get_response cannot be None in Django 4.0 and later')
            super().__init__(get_response)

    def process_request(self, request):
        if self.should_fast_skip(request):
            return None

        # Grab the user ID from the session so we avoid hitting the database
        # for the user object.
        # NOTE: We use the user ID because it's not user-settable and it won't
        #       ever change (usernames and email addresses can change)
        user_id = request.session['_auth_user_id']

        # Get the cache prefix
        key_version = cache.get('django:tos:key_version')

        # Skip if the user is allowed to skip - for instance, if the user is an
        # admin or a staff member
        if cache.get(f'django:tos:skip_tos_check:{user_id}', False, version=key_version):
            return None

        # Ping the cache for the user agreement
        user_agreed = cache.get(f'django:tos:agreed:{user_id}', None, version=key_version)

        # If the cache is missing this user
        if user_agreed is None:
            # Check the database and cache the result
            user_agreed = self.get_and_cache_agreement_from_db(user_id, key_version)

        if not user_agreed:
            # Confirm view uses these session keys. Non-middleware flow sets them in login view,
            # so we need to set them here.
            request.session['tos_user'] = user_id
            request.session['tos_backend'] = request.session['_auth_user_backend']

            response = HttpResponseRedirect('{}?{}={}'.format(
                tos_check_url,
                REDIRECT_FIELD_NAME,
                request.path_info,
            ))
            add_never_cache_headers(response)
            return response

        return None

    def should_fast_skip(self, request):
        '''Check if we should skip TOS checks without hitting the cache or database'''
        # Don't get in the way of any mutating requests
        if request.method != 'GET':
            return True

        # Ignore ajax requests
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return True

        # Don't redirect users when they're trying to get to the confirm page
        if request.path_info == tos_check_url:
            return True

        # If the user doesn't have a user ID, ignore them - they're anonymous
        if not request.session.get(session_key, None):
            return True

        return False

    def get_and_cache_agreement_from_db(self, user_id, key_version):
        # Grab the data from the database
        user_agreed = UserAgreement.objects.filter(
            user__id=user_id,
            terms_of_service__active=True).exists()

        # Set the value in the cache
        cache.set(f'django:tos:agreed:{user_id}', user_agreed, version=key_version)

        return user_agreed
