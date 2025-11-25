from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tos.models import TermsOfService, UserAgreement, has_user_agreed_latest_tos


class TestAdmin(TestCase):

    def setUp(self):
        # User that has agreed to TOS
        self.user1 = get_user_model().objects.create_user('user1', 'user1@example.com', 'user1pass', is_superuser=True, is_staff=True)
        self.user2 = get_user_model().objects.create_user('user2', 'user2@example.com', 'user2pass')
        self.user3 = get_user_model().objects.create_user('user3', 'user3@example.com', 'user3pass')

        self.tos1 = TermsOfService.objects.create(
            content="first edition of the terms of service",
            active=True,  # Will be marked as inactive as soon as tos2 is saved
        )
        self.tos2 = TermsOfService.objects.create(
            content="second edition of the terms of service",
            active=True,
        )

        self.login_url = getattr(settings, 'LOGIN_URL', '/login/')

        self.uas = UserAgreement.objects.bulk_create([
            # Everybody agreed to the original TOS
            UserAgreement(terms_of_service=self.tos1, user=self.user1),
            UserAgreement(terms_of_service=self.tos1, user=self.user2),
            UserAgreement(terms_of_service=self.tos1, user=self.user3),
            # Only user 1 and user 2 have agreed to the latest TOS
            UserAgreement(terms_of_service=self.tos2, user=self.user1),
            UserAgreement(terms_of_service=self.tos2, user=self.user2),
        ])

    def test_termsofservice_model_admin(self):
        self.client.force_login(self.user1)

        response = self.client.get(reverse('admin:tos_termsofservice_changelist'))

        self.assertEqual(len(response.context['cl'].result_list), 2)
        self.assertEqual(response.context['cl'].result_list[0], self.tos2)
        self.assertEqual(response.context['cl'].result_list[1], self.tos1)

    def test_useragreement_model_admin(self):
        self.client.force_login(self.user1)

        def find_ua(user_agreements, user=None, tos=None):
            for ua in user_agreements:
                if ua.user == user and ua.terms_of_service == tos:
                    return ua
            else:  # pragma: no cover
                return None

        response = self.client.get(reverse('admin:tos_useragreement_changelist'))

        # We don't specify a default ordering for user agreements, so we just
        # search for each one we have created
        for ua in self.uas:
            self.assertIsNotNone(find_ua(response.context['cl'].result_list, ua.user, ua.terms_of_service))
