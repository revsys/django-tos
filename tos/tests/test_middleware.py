from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from tos.compat import get_runtime_user_model
from tos.models import TermsOfService, UserAgreement


@override_settings(
    MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES + [
        'tos.middleware.UserAgreementMiddleware',
    ]
)
class TestMiddleware(TestCase):

    def setUp(self):
        # User that has agreed to TOS
        self.user1 = get_runtime_user_model().objects.create_user('user1', 'user1@example.com', 'user1pass')

        # User that has not yet agreed to TOS
        self.user2 = get_runtime_user_model().objects.create_user('user2', 'user2@example.com', 'user2pass')
        self.user3 = get_runtime_user_model().objects.create_user('user3', 'user3@example.com', 'user3pass')

        self.tos1 = TermsOfService.objects.create(
            content="first edition of the terms of service",
            active=True
        )
        self.tos2 = TermsOfService.objects.create(
            content="second edition of the terms of service",
            active=False
        )
        self.login_url = getattr(settings, 'LOGIN_URL', '/login/')

        UserAgreement.objects.create(
            terms_of_service=self.tos1,
            user=self.user1
        )

        self.redirect_page = '{0}?{1}={2}'.format(
            reverse('tos_check_tos'),
            REDIRECT_FIELD_NAME,
            reverse('index'),
        )

    def test_middleware_redirects(self):
        """
        User that hasn't accepted TOS should be redirected to confirm. Also make sure
        confirm works.
        """
        self.client.login(username='user2', password='user2pass')
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, self.redirect_page)

        # Make sure confirm works after middleware redirect.
        response = self.client.post(reverse('tos_check_tos'), {'accept': 'accept'})

        # Confirm redirects.
        self.assertEqual(response.status_code, 302)

    def test_middleware_doesnt_redirect(self):
        """User that has accepted TOS should get 200."""
        self.client.login(username='user1', password='user1pass')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_accept_after_middleware_redirects_properly(self):
        self.client.login(username='user3', password='user3pass')

        response = self.client.get(reverse('index'), follow=True)

        self.assertRedirects(response, self.redirect_page)

        # Agree
        response = self.client.post(self.redirect_page, {'accept': 'accept'})

        # Confirm redirects back to the index page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace('http://testserver', ''), str(reverse('index')))
