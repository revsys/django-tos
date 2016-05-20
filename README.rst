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

Installation
============

 1. `pip install django-tos`

 2. Add `tos` to your INSTALLED_APPS setting.

 3. Run the command `manage.py syncdb` or on newer version of Django `manage.py migrate`.

 4. In your root urlconf file `urls.py` add::

     # terms of service links
     urlpatterns += patterns('',
         url(r'^login/$', 'tos.views.login', {}, 'auth_login',),
         url(r'^terms-of-service/', include('tos.urls')),
     )


===============
django-tos-i18n
===============

django-tos internationalization using django-modeltranslation.

Installation
============

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
