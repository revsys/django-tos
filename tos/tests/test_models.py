from django.core.exceptions import ValidationError
from django.test import TestCase

from tos.compat import get_runtime_user_model
from tos.models import (
                        NoActiveTermsOfService,
                        TermsOfService,
                        UserAgreement,
                        has_user_agreed_latest_tos,
                       )


class TestModels(TestCase):

    def setUp(self):
        self.user1 = get_runtime_user_model().objects.create_user('user1',
                                                    'user1@example.com',
                                                    'user1pass')
        self.user2 = get_runtime_user_model().objects.create_user('user2',
                                                    'user2@example.com',
                                                    'user2pass')
        self.user3 = get_runtime_user_model().objects.create_user('user3',
                                                    'user3@example.com',
                                                    'user3pass')

        self.tos1 = TermsOfService.objects.create(
            content="first edition of the terms of service",
            active=True
        )
        self.tos2 = TermsOfService.objects.create(
            content="second edition of the terms of service",
            active=False
        )

    def test_terms_of_service(self):

        self.assertEquals(TermsOfService.objects.count(), 2)

        # order is by -created
        latest = TermsOfService.objects.latest()
        self.assertFalse(latest.active)

        # setting a tos to True changes all others to False
        latest.active = True
        latest.save()
        first = TermsOfService.objects.get(id=self.tos1.id)
        self.assertFalse(first.active)

        # latest is active though
        self.assertTrue(latest.active)

    def test_validation_error_all_set_false(self):
        """
        If you try and set all to false the model will throw a ValidationError
        """

        self.tos1.active = False
        self.assertRaises(ValidationError, self.tos1.save)

    def test_user_agreement(self):

        # simple agreement
        UserAgreement.objects.create(
            terms_of_service=self.tos1,
            user=self.user1
        )

        self.assertTrue(has_user_agreed_latest_tos(self.user1))
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        self.assertFalse(has_user_agreed_latest_tos(self.user3))

        # Now set self.tos2.active to True and see what happens
        self.tos2.active = True
        self.tos2.save()
        self.assertFalse(has_user_agreed_latest_tos(self.user1))
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        self.assertFalse(has_user_agreed_latest_tos(self.user3))

        # add in a couple agreements and try again
        UserAgreement.objects.create(
            terms_of_service=self.tos2,
            user=self.user1
        )
        UserAgreement.objects.create(
            terms_of_service=self.tos2,
            user=self.user3
        )

        self.assertTrue(has_user_agreed_latest_tos(self.user1))
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        self.assertTrue(has_user_agreed_latest_tos(self.user3))


class TestManager(TestCase):
    def test_terms_of_service_manager(self):

        tos1 = TermsOfService.objects.create(
            content="first edition of the terms of service",
            active=True
        )

        self.assertEquals(TermsOfService.objects.get_current_tos(), tos1)

    def test_terms_of_service_manager_raises_error(self):

        self.assertRaises(NoActiveTermsOfService, TermsOfService.objects.get_current_tos)
