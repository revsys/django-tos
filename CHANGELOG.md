# Changelog

## Unreleased

- Fix version drift: `tos/__init__.py` is synced to the packaged version and is
  tracked by bumpver going forward (#103)

## Version 1.2.0

_Released July 30th, 2026_

- Modernize packaging and tooling: move to `pyproject.toml` with the hatchling
  build backend, nox, and ruff (#102)
- Add support for Django 4.2, 5.0, 5.1, 5.2, 6.0, and 6.1
- Add support for Python 3.10 through 3.14, including free-threaded 3.14
- Convert the middleware to modern Django conventions and add tests
- Add `tos/utils.py` and expand test coverage
- Set `default_auto_field` to silence Django 3.2+ warnings
- Exclude test files from built distributions

## Version 1.1.0

_Released February 13th, 2023_

- Refactor the middleware to make extending the skip checks easier
- Fix the signal handler
- Django 3 compatibility fixes and a switch to f-strings

## Version 1.0.0

_Released January 26th, 2022_

- Python 3 only; remove the compatibility shims
- Use `gettext_lazy` instead of the removed `ugettext_lazy`
- Replace `django.conf.urls.url` with `django.urls.re_path`
- Remove the deprecated `default_app_config`

## Earlier releases

This project had no changelog before 1.2.0, so the entries below are
reconstructed from Git tags. See the
[tags](https://github.com/revsys/django-tos/tags) for the full diffs.

- **0.9.0** — October 8th, 2020
- **0.8.1** — July 29th, 2020
- **0.8.0** — July 29th, 2020
- **0.7.0** — August 11th, 2016
- **0.5.0** — May 20th, 2016
