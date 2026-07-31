# django-tos

[![CI](https://github.com/revsys/django-tos/actions/workflows/actions.yml/badge.svg)](https://github.com/revsys/django-tos/actions/workflows/actions.yml)
[![PyPI](https://img.shields.io/pypi/v/django-tos.svg)](https://pypi.org/project/django-tos/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-tos.svg)](https://pypi.org/project/django-tos/)
[![Django versions](https://img.shields.io/pypi/frameworkversions/django/django-tos.svg)](https://pypi.org/project/django-tos/)

This project gives the admin the ability to reset terms of agreement with the end users. It tracks when TOS are changed and when users agree to the new TOS.

## Summary

- Keeps track of when TOS is changed
- Users need to be informed and agree/re-agree when they login (custom login is provided)
- Just two models (TOS and user agreement)

## Requirements

Supports Django 4.2, 5.0, 5.1, 5.2, 6.0, and 6.1 on Python 3.10 through 3.14
(including free-threaded 3.14).

`django-tos` also relies on `AUTH_USER_MODEL` (the `UserAgreement` foreign key)
and `LOGIN_REDIRECT_URL` (the post-agreement redirect fallback).

## Terms Of Service Installation

1. `pip install django-tos`
2. Add `tos` to your `INSTALLED_APPS` setting.
3. Sync your database with `python manage.py migrate`

## Creating a Terms of Service

`django-tos` needs an **active** `TermsOfService` to check users against. Create
one in the Django admin (or via a data migration / fixture) and mark it active.
Saving a new active `TermsOfService` automatically deactivates the previous one.

If no active terms exist, `django-tos` warns when `DEBUG` is `True` and raises
`tos.models.NoActiveTermsOfService` when `DEBUG` is `False`. A fresh database in
development therefore will not crash, while a misconfigured production deploy
fails loudly rather than silently skipping the check.

## Configuration

### Options

There are two ways to configure `django-tos` - either enable the TOS check when users sign in, or use middleware to enable the TOS check on every `GET` request.

If you cannot override your login view (for instance, if you're using [django-allauth](https://django-allauth.readthedocs.io/en/latest/)) you should use the second option.

### Option 1: TOS Check On Sign In

In your root urlconf file `urls.py` add:

```python
from django.urls import include, path, re_path

from tos.views import login

# terms of service links
urlpatterns += [
    re_path(r'^login/$', login, name='auth_login'),
    path('terms-of-service/', include('tos.urls')),
]
```

### Option 2: Middleware Check

This option uses the `incr` methods for the configured Django cache. If you are using `django-tos` in a complex or parallel environment, be sure to use a cache backend that supports atomic increment operations. For more information, see the notes at the end of [this section of the Django documentation](https://docs.djangoproject.com/en/4.2/topics/cache/#basic-usage).

Also, to ensure that warming the cache with users who can skip the agreement check works properly, you will need to include `tos` before your own apps in your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = (
    ...
    'tos',
    # your own apps come after tos
    ...
)
```

#### Advantages

- Can optionally use a separate cache for TOS agreements (necessary if your default cache does not support atomic increment operations)
- Allow some of your users to skip the TOS check (eg: developers, staff, admin, superusers, employees)
- Uses signals to invalidate cached agreements
- Skips the agreement check when the user is anonymous or not signed in
- Skips the agreement check when the request is AJAX
- Skips the agreement check when the request isn't a `GET` request (to avoid getting in the way of data mutations)

#### Disadvantages

- Requires a cache key for each user who is signed in
- Requires an additional cache key for each staff user
- May leave keys in the cache when the active `TermsOfService` changes

#### Efficiency

- Best case for staff users: 2 cache hits
- Best case for non-staff users: 1 cache miss, 2 cache hits
- Worst case: 1 cache hit, 2 cache misses, 1 database query, 1 cache set (this should only happen when the user signs in)

#### Option 2 Configuration

1. In your root urlconf file `urls.py` only add the terms-of-service URLs:

   ```python
   # terms of service links
   urlpatterns += [
       path('terms-of-service/', include('tos.urls')),
   ]
   ```

2. Optional: Since the cache used by TOS will be overwhelmingly read-heavy, you can use a separate cache specifically for TOS. To do so, create a new cache in your project's `settings.py`:

   ```python
   CACHES = {
       ...
       # The cache specifically for django-tos
       'tos': {  # Can use any name here
           'BACKEND': ...,
           'LOCATION': ...,
           'NAME': 'tos-cache',  # Can use any name here
       },
   }
   ```

   and configure `django-tos` to use the new cache:

   ```python
   TOS_CACHE_NAME = 'tos'  # Must match the key name in CACHES
   ```

   this setting defaults to the `default` cache.

3. Then in your project's `settings.py` add the middleware to `MIDDLEWARE`:

   ```python
   MIDDLEWARE = (
       ...
       # Terms of service checks
       'tos.middleware.UserAgreementMiddleware',
   )
   ```

4. Optional: To allow users to skip the TOS check, you will need to set corresponding cache keys for them in the TOS cache. The cache key for each user will need to be prefixed with `django:tos:skip_tos_check:`, and have the user ID appended to it.

   Here is an example app configuration that allows staff users and superusers to skip the TOS agreement check:

   ```python
   from django.apps import AppConfig, apps
   from django.conf import settings
   from django.contrib.auth import get_user_model
   from django.db.models.signals import post_save

   class MyAppConfig(AppConfig):
       name = 'myapp'

       def ready(self):
           if 'tos' in settings.INSTALLED_APPS:
               from tos.utils import add_staff_users_to_tos_cache, set_staff_in_cache_for_tos
               tos_app = apps.get_app_config('tos')
               TermsOfService = tos_app.get_model('TermsOfService')

               post_save.connect(set_staff_in_cache_for_tos, sender=get_user_model(), dispatch_uid='set_staff_in_cache_for_tos')

               post_save.connect(add_staff_users_to_tos_cache, sender=TermsOfService, dispatch_uid='add_staff_users_to_tos_cache')
   ```

# django-tos-i18n

django-tos internationalization using django-modeltranslation.

## Terms Of Service i18n Installation

Assuming you have correctly installed django-tos in your app you only need to
add following apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS += ('modeltranslation', 'tos_i18n')
```

You should also define your languages in Django's `LANGUAGES` setting, e.g.:

```python
LANGUAGES = (
    ('pl', 'Polski'),
    ('en', 'English'),
)
```

Please note that adding those to `INSTALLED_APPS` **changes** Django models: for
every registered field that should be translated, it adds fields named
`field_<lang_code>`. For example, given this model:

```python
class MyModel(models.Model):
    name = models.CharField(max_length=10)
```

the following fields are generated: `name`, `name_en`, `name_pl`.

That's it. You are now running tos in i18n mode with the languages you declared
in `LANGUAGES` setting. This will also make all required adjustments in the
Django admin.

For more info on how translation works in details please refer to the
[django-modeltranslation documentation](https://django-modeltranslation.readthedocs.org/en/latest/).
