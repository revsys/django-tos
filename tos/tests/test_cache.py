from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from tos.models import TermsOfService, UserAgreement, has_user_agreed_latest_tos
from tos.utils import (
    add_staff_users_to_tos_cache,
    get_tos_cache,
    initialize_cache_version,
    set_staff_in_cache_for_tos,
)


class CacheTestCase(TestCase):
    def setUp(self):
        self.cache = get_tos_cache()
        self.cache.clear()

        User = get_user_model()
        User.objects.bulk_create([
            User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                is_staff=True if i < 3 else False,
                is_superuser=True if i % 2 == 0 else False,
            )
            for i in range(1, 10)
        ])

    def get_skip_tos_check(self, i: int):
        return self.cache.get(
            f"django:tos:skip_tos_check:{i}",
            None,
            version=self.cache.get('django:tos:key_version'),
        )

    def call_command(self, cmd, *args, **kwargs):
        out = StringIO()
        err = StringIO()
        call_command(
            cmd,
            *args,
            stdout=out,
            stderr=err,
            **kwargs,
        )
        return out.getvalue(), err.getvalue()

    def test_command(self):
        for i in range(1, 10):
            self.assertIsNone(self.get_skip_tos_check(i))

        out, _ = self.call_command("add_staff_users_to_tos_cache")

        self.assertIn("Successfully added staff users to TOS staff", out)

        for i in range(1, 3):
            self.assertIsNotNone(self.get_skip_tos_check(i))
        for i in range(2, 10, 2):
            self.assertIsNotNone(self.get_skip_tos_check(i))
        for i in range(3, 10, 2):
            self.assertIsNone(self.get_skip_tos_check(i))

    def test_initialize_cache_version(self):
        self.assertIsNone(self.cache.get('django:tos:key_version'))

        initialize_cache_version()

        self.assertIsNotNone(self.cache.get('django:tos:key_version', None))
        self.assertEqual(self.cache.get('django:tos:key_version'), 1)

        initialize_cache_version()

        self.assertIsNotNone(self.cache.get('django:tos:key_version', None))
        self.assertEqual(self.cache.get('django:tos:key_version'), 1)

    def test_add_staff_users_to_tos_cache(self):
        self.assertIsNone(add_staff_users_to_tos_cache(raw=True))

        add_staff_users_to_tos_cache()

        for i in range(1, 3):
            self.assertIsNotNone(self.get_skip_tos_check(i))
        for i in range(2, 10, 2):
            self.assertIsNotNone(self.get_skip_tos_check(i))
        for i in range(3, 10, 2):
            self.assertIsNone(self.get_skip_tos_check(i))

    def test_set_staff_in_cache_for_tos(self):
        self.assertIsNone(set_staff_in_cache_for_tos(instance=None, raw=True))

        User = get_user_model()
        for i in range(1, 10):
            set_staff_in_cache_for_tos(instance=User.objects.get(id=i))
            if i < 3:
                self.assertTrue(self.get_skip_tos_check(i))
            if i % 2 == 0:
                self.assertTrue(self.get_skip_tos_check(i))
            if not (i < 3 or i % 2 == 0):
                self.assertIsNone(self.get_skip_tos_check(i))

                # Set it manually again, then run set again to ensure it
                # removes the user from the skip cache when they are removed as
                # a staff and superuser
                self.cache.set(f"django:tos:skip_tos_check:{i}", True, version=self.cache.get("django:tos:key_version"))
                set_staff_in_cache_for_tos(instance=User.objects.get(id=i))
                self.assertIsNone(self.get_skip_tos_check(i))
