from django.core.management.base import BaseCommand

from tos.utils import add_staff_users_to_tos_cache


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_staff_users_to_tos_cache()
        self.stdout.write(
            self.style.SUCCESS("Successfully added staff users to TOS staff")
        )
