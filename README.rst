==========
django-tos
==========

.. image:: https://secure.travis-ci.org/revsys/django-tos.png
    :alt: Build Status
    :target: http://travis-ci.org/revsys/django-tos

This project gives the admin the ability to reset terms of agreement with the end users. It tracks when TOS are changed and when users agree to the new TOS.

Summary
=======

    - Keeps track of when TOS is changed
    - Users need to be informed and agree/re-agree when they login (custom login is provided)
    - Just two models (TOS and user agreement)

Terms Of Service Installation
=============================

 1. `pip install django-tos`

 2. Add `tos` to your `INSTALLED_APPS` setting.

 3. Sync your database with `python manage.py migrate` or `python manage.py syncdb` for Django < 1.7.

Configuration
=============

Options
```````

There are two ways to configure `django-tos` - either enable the TOS check when users sign in, or use middleware to enable the TOS check on every `GET` request.

If you cannot override your login view (for instance, if you're using `django-allauth <https://django-allauth.readthedocs.io/en/latest/>`_) you should use the second option.

There are some additional advantages of using the middleware option:

* Allow some of your users to skip the TOS check (eg: developers, staff, admin, superusers, employees)
* Best case for staff users: 1 cache hit
* Best case for non-staff users: 1 cache miss, 1 cache hit
* Uses signals to invalidate cached agreements
* Skips the agreement check when the user is anonymous or not signed in
* Skips the agreement check when the request is AJAX
* Skips the agreement check when the request isn't a `GET` request (to avoid getting in the way of data mutations)
  
But there are some disadvantages:

* Worst case: 1 cache miss, 1 database query, 1 cache set (this should only happen when the user signs in)
* Requires a separate cache for `django-tos` because...
* Invalidates **entire** TOS cache when `TermsOfService` is changed
* Requires a cache key for each user who is signed in
* Requires an additional cache key for each staff user

Because of this, the middleware is 100% optional.

TOS Check On Login
``````````````````

In your root urlconf file `urls.py` add::

    # terms of service links
    urlpatterns += patterns('',
        url(r'^login/$', 'tos.views.login', {}, 'auth_login',),
        url(r'^terms-of-service/', include('tos.urls')),
    )

Middleware Check
````````````````

1. In your root urlconf file `urls.py` only add the terms-of-service URLs::

    # terms of service links
    urlpatterns += patterns('',
        url(r'^terms-of-service/', include('tos.urls')),
    )

2. It is strongly recommended to use a cache specifically for `django-tos`, because it clears ALL keys in the configured cache when `TermsOfService` objects change. Create a new cache in your project's `settings.py`::
   
       CACHES = {
           ...
           # The cache to use specifically for django-tos
           'tos': {  # Can use any name
               'BACKEND': ...,
               'LOCATION': ...,
               'NAME': 'tos-cache',  # Can use any name
           },
       }

3. Configure `django-tos` to use the cache::

       TOS_CACHE_NAME = 'tos'  # Much match the key name in in `CACHES`.

4. Then in your project's `settings.py` add the middleware to `MIDDLEWARE_CLASSES`::

    MIDDLEWARE_CLASSES = (
        ...
        # Terms of service checks
        'tos.middleware.UserAgreementMiddleware',
    )

5. To allow users to skip the TOS check, you will need to set corresponding cache keys for them in the TOS cache. The cache key for each user will need to be prefixed with 'django:tos:skip_tos_check:', and have the user ID appended to it.

   Here is an example app configuration that allows staff users and superusers to skip the tos check:

   .. code-block:: python

    from django.apps import AppConfig, apps
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.cache import caches
    from django.db.models import Q
    from django.db.models.signals import post_save, pre_save
    from django.dispatch import receiver

    class MyAppConfig(AppConfig):
        def ready(self):
            if 'tos' in settings.INSTALLED_APPS:
                cache = caches[getattr(settings, 'TOS_CACHE_NAME')]
                tos_app = apps.get_app_config('tos')
                TermsOfService = tos_app.get_model('TermsOfService')

                @receiver(post_save, sender=get_user_model(), dispatch_uid='set_staff_in_cache_for_tos')
                def set_staff_in_cache_for_tos(user, instance, **kwargs):
                    if kwargs.get('raw', False):
                        return

                    # If the user is staff allow them to skip the TOS agreement check
                    if instance.is_staff or instance.is_superuser:
                        cache.set('django:tos:skip_tos_check:{}'.format(instance.id))

                    # But if they aren't make sure we invalidate them from the cache
                    elif cache.get('django:tos:skip_tos_check:{}'.format(instance.id), False):
                        cache.delete('django:tos:skip_tos_check:{}'.format(instance.id))

                @receiver(post_save, sender=TermsOfService, dispatch_uid='add_staff_users_to_tos_cache')
                def add_staff_users_to_tos_cache(*args, **kwargs):
                    if kwargs.get('raw', False):
                        return

                    # Efficiently cache all of the users who are allowed to skip the TOS
                    # agreement check
                    cache.set_many({
                        'django:tos:skip_tos_check:{}'.format(staff_user.id): True
                        for staff_user in get_user_model().objects.filter(
                            Q(is_staff=True) | Q(is_superuser=True))
                    })

                # Immediately add staff users to the cache
                add_staff_users_to_tos_cache()

===============
django-tos-i18n
===============

django-tos internationalization using django-modeltranslation.

Terms Of Service i18n Installation
==================================

Assuming you have correctly installed django-tos in your app you only need to
add following apps to ``INSTALLED_APPS``::

    INSTALLED_APPS += ('modeltranslation', 'tos_i18n')

and also you should also define your languages in Django ``LANGUAGES``
variable, eg.::

    LANGUAGES = (
        ('pl', 'Polski'),
        ('en', 'English'),
    )

Please note that adding those to ``INSTALLED_APPS`` **changes** Django models.
Concretely it adds for every registered ``field`` that should translated,
additional fields with name ``field_<lang_code>``, e.g. for given model::

    class MyModel(models.Model):
        name = models.CharField(max_length=10)

There will be generated fields: ``name`` , ``name_en``, ``name_pl``.

You should probably migrate your database, using South is recommended.
Migrations should be kept in your local project.


How to migrate tos with South
`````````````````````````````

Here is some step-by-step example how to convert your legacy django-tos
instalation synced using syncdb into a translated django-tos-i18n with South
migrations.

1. Inform South that you want to store migrations in custom place by putting
   this in your Django settings file::

    SOUTH_MIGRATION_MODULES = {
        'tos': 'YOUR_APP.migrations.tos',
    }

2. Add required directory (package)::

    mkdir -p YOUR_APP/migrations/tos
    touch YOUR_APP/migrations/tos/__init__.py

3. Create initial migration (referring to the database state as it is now)::

    python manage.py schemamigration --initial tos

4. Fake migration (because the changes are already in the database)::

    python manage.py migrate tos --fake

5. Install tos_i18n (and modeltranslation) to ``INSTALLED_APPS``::

    INSTALLED_APPS += ('modeltranslation', 'tos_i18n',)

6. Make sure that the Django LANGUAGES setting is properly configured.

7. Migrate what changed::

    $ python manage.py schemamigration --auto tos
    $ python migrate tos


That's it. You are now running tos in i18n mode with the languages you declared
in ``LANGUAGES`` setting. This will also make all required adjustments in the
Django admin.

For more info on how translation works in details please refer to the
`django-modeltranslation documentation
<https://django-modeltranslation.readthedocs.org/en/latest/>`_.
