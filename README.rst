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

1. ``pip install django-tos``

2. Add ``tos`` to your ``INSTALLED_APPS`` setting.

3. Sync your database with ``python manage.py migrate`` or ``python manage.py syncdb`` for Django < 1.7.

Configuration
=============

Options
```````

There are two ways to configure ``django-tos`` - either enable the TOS check when users sign in, or use middleware to enable the TOS check on every ``GET`` request.

If you cannot override your login view (for instance, if you're using `django-allauth <https://django-allauth.readthedocs.io/en/latest/>`_) you should use the second option.

Option 1: TOS Check On Sign In
``````````````````````````````

In your root urlconf file ``urls.py`` add:

.. code-block:: python

    from tos.views import login

    # terms of service links
    urlpatterns += patterns('',
        url(r'^login/$', login, {}, 'auth_login',),
        url(r'^terms-of-service/', include('tos.urls')),
    )

Option 2: Middleware Check
``````````````````````````

This option uses the ``incr`` methods for the configured Django cache. If you are using ``django-tos`` in a complex or parallel environment, be sure to use a cache backend that supports atomic increment operations. For more information, see the notes at the end of `this section of the Django documentation <https://docs.djangoproject.com/en/1.9/topics/cache/#basic-usage>`_.

Also, to ensure that warming the cache with users who can skip the agreement check works properly, you will need to include ``tos`` before your app (``myapp`` in the example) in your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'tos',
        ...
        'myapp',  # Example app name
        ...
    )

Advantages
----------

* Can optionally use a separate cache for TOS agreements (necessary if your default cache does not support atomic increment operations)
* Allow some of your users to skip the TOS check (eg: developers, staff, admin, superusers, employees)
* Uses signals to invalidate cached agreements
* Skips the agreement check when the user is anonymous or not signed in
* Skips the agreement check when the request is AJAX
* Skips the agreement check when the request isn't a ``GET`` request (to avoid getting in the way of data mutations)
  
Disadvantages
-------------

* Requires a cache key for each user who is signed in
* Requires an additional cache key for each staff user
* May leave keys in the cache when the active ``TermsOfService`` changes

Efficiency
----------

* Best case for staff users: 2 cache hits
* Best case for non-staff users: 1 cache miss, 2 cache hits
* Worst case: 1 cache hit, 2 cache misses, 1 database query, 1 cache set (this should only happen when the user signs in)

Option 2 Configuration
----------------------

1. In your root urlconf file ``urls.py`` only add the terms-of-service URLs:

   .. code-block:: python

       # terms of service links
       urlpatterns += patterns('',
           url(r'^terms-of-service/', include('tos.urls')),
       )

2. Optional: Since the cache used by TOS will be overwhelmingly read-heavy, you can use a separate cache specifically for TOS. To do so, create a new cache in your project's ``settings.py``:

   .. code-block:: python
   
       CACHES = {
           ...
           # The cache specifically for django-tos
           'tos': {  # Can use any name here
               'BACKEND': ...,
               'LOCATION': ...,
               'NAME': 'tos-cache',  # Can use any name here
           },
       }

   and configure ``django-tos`` to use the new cache:

   .. code-block:: python

       TOS_CACHE_NAME = 'tos'  # Must match the key name in in CACHES

   this setting defaults to the ``default`` cache.

4. Then in your project's ``settings.py`` add the middleware to ``MIDDLEWARE_CLASSES``:

   .. code-block:: python

       MIDDLEWARE_CLASSES = (
           ...
           # Terms of service checks
           'tos.middleware.UserAgreementMiddleware',
       )

5. Optional: To allow users to skip the TOS check, you will need to set corresponding cache keys for them in the TOS cache. The cache key for each user will need to be prefixed with ``django:tos:skip_tos_check:``, and have the user ID appended to it.

   Here is an example app configuration that allows staff users and superusers to skip the TOS agreement check:

   .. code-block:: python

       from django.apps import AppConfig, apps
       from django.conf import settings
       from django.contrib.auth import get_user_model
       from django.core.cache import caches
       from django.db.models import Q
       from django.db.models.signals import post_save, pre_save
       from django.dispatch import receiver

       class MyAppConfig(AppConfig):
           name = 'myapp'

           def ready(self):
               if 'tos' in settings.INSTALLED_APPS:
                   cache = caches[getattr(settings, 'TOS_CACHE_NAME', 'default')]
                   tos_app = apps.get_app_config('tos')
                   TermsOfService = tos_app.get_model('TermsOfService')

                   @receiver(post_save, sender=get_user_model(), dispatch_uid='set_staff_in_cache_for_tos')
                   def set_staff_in_cache_for_tos(user, instance, **kwargs):
                       if kwargs.get('raw', False):
                           return

                       # Get the cache prefix
                       key_version = cache.get('django:tos:key_version')

                       # If the user is staff allow them to skip the TOS agreement check
                       if instance.is_staff or instance.is_superuser:
                           cache.set('django:tos:skip_tos_check:{}'.format(instance.id), version=key_version)

                       # But if they aren't make sure we invalidate them from the cache
                       elif cache.get('django:tos:skip_tos_check:{}'.format(instance.id), False):
                           cache.delete('django:tos:skip_tos_check:{}'.format(instance.id), version=key_version)

                   @receiver(post_save, sender=TermsOfService, dispatch_uid='add_staff_users_to_tos_cache')
                   def add_staff_users_to_tos_cache(*args, **kwargs):
                       if kwargs.get('raw', False):
                           return

                       # Get the cache prefix
                       key_version = cache.get('django:tos:key_version')

                       # Efficiently cache all of the users who are allowed to skip the TOS
                       # agreement check
                       cache.set_many({
                           'django:tos:skip_tos_check:{}'.format(staff_user.id): True
                           for staff_user in get_user_model().objects.filter(
                               Q(is_staff=True) | Q(is_superuser=True))
                       }, version=key_version)

                   # Immediately add staff users to the cache
                   add_staff_users_to_tos_cache()

===============
django-tos-i18n
===============

django-tos internationalization using django-modeltranslation.

Terms Of Service i18n Installation
==================================

Assuming you have correctly installed django-tos in your app you only need to
add following apps to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS += ('modeltranslation', 'tos_i18n')

and also you should also define your languages in Django ``LANGUAGES``
variable, e.g.:

.. code-block:: python

    LANGUAGES = (
        ('pl', 'Polski'),
        ('en', 'English'),
    )

Please note that adding those to ``INSTALLED_APPS`` **changes** Django models.
Concretely it adds for every registered ``field`` that should translated,
additional fields with name ``field_<lang_code>``, e.g. for given model:

.. code-block:: python

    class MyModel(models.Model):
        name = models.CharField(max_length=10)

There will be generated fields: ``name`` , ``name_en``, ``name_pl``.

You should probably migrate your database, and if you're using Django < 1.7 using South is recommended. These migrations should be kept in your local project.

How to migrate tos with South
`````````````````````````````

Here is some step-by-step example how to convert your legacy django-tos
instalation synced using syncdb into a translated django-tos-i18n with South
migrations.

1. Inform South that you want to store migrations in custom place by putting
   this in your Django settings file:

   .. code-block:: python

       SOUTH_MIGRATION_MODULES = {
           'tos': 'YOUR_APP.migrations.tos',
       }

2. Add required directory (package):

   .. code-block:: bash

       mkdir -p YOUR_APP/migrations/tos
       touch YOUR_APP/migrations/tos/__init__.py

3. Create initial migration (referring to the database state as it is now):

   .. code-block:: bash

       python manage.py schemamigration --initial tos

4. Fake migration (because the changes are already in the database):

   .. code-block:: bash

       python manage.py migrate tos --fake

5. Install tos_i18n (and modeltranslation) to ``INSTALLED_APPS``:

   .. code-block:: python

       INSTALLED_APPS += ('modeltranslation', 'tos_i18n',)

6. Make sure that the Django ``LANGUAGES`` setting is properly configured.

7. Migrate what changed:

   .. code-block:: bash

    $ python manage.py schemamigration --auto tos
    $ python migrate tos


That's it. You are now running tos in i18n mode with the languages you declared
in ``LANGUAGES`` setting. This will also make all required adjustments in the
Django admin.

For more info on how translation works in details please refer to the
`django-modeltranslation documentation
<https://django-modeltranslation.readthedocs.org/en/latest/>`_.
