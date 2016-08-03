from django.conf import settings
from django.contrib.auth import SESSION_KEY as session_key
from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.cache import add_never_cache_headers

from .models import UserAgreement

cache = caches[getattr(settings, 'TOS_CACHE_NAME', 'default')]
tos_check_url = reverse('tos_check_tos')


class UserAgreementMiddleware(object):
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
        user_id = request.session.get(session_key)

        # Get the cache prefix
        key_version = cache.get('django:tos:key_version')

        # Skip if the user is allowed to skip - for instance, if the user is an
        # admin or a staff member
        if cache.get('django:tos:skip_tos_check:{}'.format(str(user_id)), False, version=key_version):
            return None

        # Ping the cache for the user agreement
        user_agreed = cache.get('django:tos:agreed:{}'.format(str(user_id)), None, version=key_version)

        # If the cache is missing this user
        if user_agreed is None:
            # Grab the data from the database
            user_agreed = UserAgreement.objects.filter(
                user__id=user_id,
                terms_of_service__active=True).exists()

            # Set the value in the cache
            cache.set('django:tos:agreed:{}'.format(user_id), user_agreed, version=key_version)

        if not user_agreed:
            return add_never_cache_headers(HttpResponseRedirect(tos_check_url))

        return None
