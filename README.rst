==========
django-tos
==========

This project gives the admin the ability to reset terms of agreement with the end users. It tracks when TOS are changed and when users agree to the new TOS.

Summary
=======

    - based flatpage
    - keep track of when TOS is changed
    - Users need to be informed and reagree when they relogin (custom login)
    - 2 models likely (TOS table and user re-agree)
    
Installation
============

django-tos relies on django-flatpages so you have to follow those rules of installation:

 1. Install the sites framework by adding `django.contrib.sites` to your INSTALLED_APPS setting, if it’s not already in there.
 
 2. Also make sure you’ve correctly set `SITE_ID` to the ID of the site the settings file represents. This will usually be 1 (i.e. `SITE_ID = 1`, but if you’re using the sites framework to manage multiple sites, it could be the ID of a different site.
 
 3. Add `django.contrib.flatpages` to your INSTALLED_APPS setting.
 
 4. Add `tos` to your INSTALLED_APPS setting.

 5. Add `django.contrib.flatpages.middleware.FlatpageFallbackMiddleware` to your MIDDLEWARE_CLASSES setting.

 5. Run the command `manage.py syncdb`.