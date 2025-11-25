from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from tos.models import (
    NoActiveTermsOfService,
    TermsOfService,
    UserAgreement,
    has_user_agreed_latest_tos,
)


class TestModels(TestCase):

    def setUp(self):
        self.user1 = get_user_model().objects.create_user('user1',
                                                    'user1@example.com',
                                                    'user1pass')
        self.user2 = get_user_model().objects.create_user('user2',
                                                    'user2@example.com',
                                                    'user2pass')
        self.user3 = get_user_model().objects.create_user('user3',
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

        self.assertEqual(TermsOfService.objects.count(), 2)

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

        self.assertEqual(str(first), f"{first.created}: inactive")
        self.assertEqual(str(latest), f"{latest.created}: active")

    def test_validation_error_all_set_false(self):
        """
        If you try and set all to false the model will throw a ValidationError
        """

        self.tos1.active = False
        self.assertRaises(ValidationError, self.tos1.save)

    def test_user_agreement(self):

        # simple agreement
        ua_u1_tos1 = UserAgreement.objects.create(
            terms_of_service=self.tos1,
            user=self.user1
        )

        self.assertTrue(has_user_agreed_latest_tos(self.user1))
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        self.assertFalse(has_user_agreed_latest_tos(self.user3))

        self.assertEqual(str(ua_u1_tos1), f"{self.user1.username} agreed to TOS: {ua_u1_tos1.terms_of_service.created}: active")

        # Now set self.tos2.active to True and see what happens
        self.tos2.active = True
        self.tos2.save()
        self.assertFalse(has_user_agreed_latest_tos(self.user1))
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        self.assertFalse(has_user_agreed_latest_tos(self.user3))

        # add in a couple agreements and try again
        ua_u1_tos2 = UserAgreement.objects.create(
            terms_of_service=self.tos2,
            user=self.user1
        )
        ua_u3_tos2 = UserAgreement.objects.create(
            terms_of_service=self.tos2,
            user=self.user3
        )

        self.assertTrue(has_user_agreed_latest_tos(self.user1))
        self.assertFalse(has_user_agreed_latest_tos(self.user2))
        self.assertTrue(has_user_agreed_latest_tos(self.user3))

        ua_u1_tos1.refresh_from_db()
        self.assertEqual(str(ua_u1_tos1), f"{self.user1.username} agreed to TOS: {ua_u1_tos1.terms_of_service.created}: inactive")
        self.assertEqual(str(ua_u1_tos2), f"{self.user1.username} agreed to TOS: {ua_u1_tos2.terms_of_service.created}: active")
        self.assertEqual(str(ua_u3_tos2), f"{self.user3.username} agreed to TOS: {ua_u3_tos2.terms_of_service.created}: active")


class TestManager(TestCase):
    def test_terms_of_service_manager(self):

        tos1 = TermsOfService.objects.create(
            content="first edition of the terms of service",
            active=True
        )

        self.assertEqual(TermsOfService.objects.get_current_tos(), tos1)

    def test_terms_of_service_manager_raises_error(self):

        self.assertRaises(NoActiveTermsOfService, TermsOfService.objects.get_current_tos)


class TestNoActiveTOS(TestCase):
    @classmethod
    def setUpClass(cls):
        # Use bulk_create to avoid calling the model's save() method
        TermsOfService.objects.bulk_create([
            TermsOfService(
                content="The only TOS",
                active=False,
            )
        ])

    @classmethod
    def tearDownClass(cls):
        TermsOfService.objects.all().delete()

    @override_settings(DEBUG=True)
    def test_model_save_raises_warning(self):
        with self.assertWarns(Warning):
            TermsOfService.objects.first().save()

    @override_settings(DEBUG=True)
    def test_get_current_tos_raises_warning(self):
        with self.assertWarns(Warning):
            TermsOfService.objects.get_current_tos()

    @override_settings(DEBUG=False)
    def test_model_save_raises_exception(self):
        with self.assertRaises(NoActiveTermsOfService):
            TermsOfService.objects.first().save()

    @override_settings(DEBUG=False)
    def test_get_current_tos_raises_exception(self):
        with self.assertRaises(NoActiveTermsOfService):
            TermsOfService.objects.get_current_tos()
