from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from tos.compat import get_runtime_user_model
from tos.models import TermsOfService, UserAgreement, has_user_agreed_latest_tos


class TestViews(TestCase):

    def setUp(self):
        # User that has agreed to TOS
        self.user1 = get_runtime_user_model().objects.create_user('user1', 'user1@example.com', 'user1pass')

        # User that has not yet agreed to TOS
        self.user2 = get_runtime_user_model().objects.create_user('user2', 'user2@example.com', 'user2pass')

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

    def test_login(self):
        """ Make sure we didn't break the authentication system
            This assumes that login urls are named 'login'
        """

        self.assertTrue(has_user_agreed_latest_tos(self.user1))
        login = self.client.login(username='user1', password='user1pass')
        self.failUnless(login, 'Could not log in')
        self.assertTrue(has_user_agreed_latest_tos(self.user1))

    def test_user_agrees_multiple_times(self):
        login_response = self.client.post(reverse('login'), {
            'username': 'user2',
            'password': 'user2pass',
        })

        self.assertTrue(login_response)

        response = self.client.post(reverse('tos_check_tos'), {'accept': 'accept'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserAgreement.objects.filter(user=self.user2).count(), 1)

        response = self.client.post(reverse('tos_check_tos'), {'accept': 'accept'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserAgreement.objects.filter(user=self.user2).count(), 1)

        response = self.client.post(reverse('tos_check_tos'), {'accept': 'accept'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserAgreement.objects.filter(user=self.user2).count(), 1)

    def test_need_agreement(self):
        """ user2 tries to login and then has to go and agree to terms"""

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        response = self.client.post(self.login_url, dict(username='user2', password='user2pass'))
        self.assertContains(response, "first edition of the terms of service")

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

    def test_do_not_need_agreement(self):
        """ user2 tries to login and has already agreed"""

        self.assertTrue(has_user_agreed_latest_tos(self.user1))

        response = self.client.post(self.login_url, dict(username='user1',
            password='user1pass'))
        self.assertEqual(302, response.status_code)

    def test_redirect_security(self):
        """ redirect to outside url not allowed, should redirect to login url"""

        response = self.client.post(self.login_url, dict(username='user1',
            password='user1pass', next='http://example.com'))
        self.assertEqual(302, response.status_code)
        self.assertIn(settings.LOGIN_REDIRECT_URL, response._headers['location'][1])

    def test_need_to_log_in(self):
        """ GET to login url shows login tempalte."""

        response = self.client.get(self.login_url)
        self.assertContains(response, "Dummy login template.")

    def test_root_tos_view(self):

        response = self.client.get('/tos/')
        self.assertIn(b'first edition of the terms of service', response.content)

    def test_reject_agreement(self):

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        response = self.client.post(self.login_url, dict(username='user2', password='user2pass'))
        self.assertContains(response, "first edition of the terms of service")
        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'reject'})

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

    def test_accept_agreement(self):

        self.assertFalse(has_user_agreed_latest_tos(self.user2))

        response = self.client.post(self.login_url, dict(username='user2', password='user2pass'))
        self.assertContains(response, "first edition of the terms of service")
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'accept'})

        self.assertTrue(has_user_agreed_latest_tos(self.user2))

    def test_bump_new_agreement(self):

        # Change the tos
        self.tos2.active = True
        self.tos2.save()

        # is user1 agreed now?
        self.assertFalse(has_user_agreed_latest_tos(self.user1))

        # user1 agrees again
        response = self.client.post(self.login_url, dict(username='user1', password='user1pass'))
        self.assertContains(response, "second edition of the terms of service")
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        url = reverse('tos_check_tos')
        response = self.client.post(url, {'accept': 'accept'})

        self.assertTrue(has_user_agreed_latest_tos(self.user1))
