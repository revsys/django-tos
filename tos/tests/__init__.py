import django

if django.VERSION < (1, 6):
    from tos.tests.test_models import *
    from tos.tests.test_views import *
