==========
django-tos
==========

This project gives the admin the ability to reset terms of agreement with the end users. It tracks when TOS are changed and when users agree to the new TOS.

Summary
=======

    - keeps track of when TOS is changed
    - Users need to be informed and agree/re-agree when they login (custom login is provided)
    - Just two models (TOS and user agreement)
    
Installation
============
 
 1. Add `tos` to your INSTALLED_APPS setting.

 2. Run the command `manage.py syncdb`.
 
 3. In your root urlconf file `urls.py` add `(r'^login/$', 'tos.views.login', {}, 'login',),` to your url patterns.
 
 4. In your root urlconf file `urls.py` add `(r'^terms-of-service/$', 'tos.views.tos', {}, 'tos',),` to your url patterns.