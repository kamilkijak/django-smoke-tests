# CHANGELOG

## 2.1.0 - 09/04/2022
- improve how allowed and disallowed status codes are handled, improve a default rule

## 2.0.0 - 07/04/2022 
- drop support for Django 1.x, leave support for 2.2 LTS, 3.2 LTS only
- drop support for Python 2.x
- fix [#15] - incorrect URLs generated for django2 style path() with parameters 
- fix [#17] - support namespaces in SKIP_SMOKE_TESTS

## 1.0.1 - 07/08/2018
- fix documentation

## 1.0.0 - 06/08/2018
- add support for Django 2.1

## 0.4.1 - 12/02/2018
- fix [#5] - use `get_user_model()`

## 0.4.0 - 22/01/2018
- add `--fixture` parameter

## 0.3.0 - 21/01/2018
- add parameters:
  * `--settings`
  * `--configuration`
  * `--no-migrations`

## 0.2.2 - 16/01/2018
- improve skipping smoke tests

## 0.2.1 - 16/01/2018
- fix [#2] - wrong exception handling

## 0.2.0 - 14/01/2018
- add support for Django 2.0
- add `--get-only` parameter

## 0.1.4 - 09/12/2017
- improve README

## 0.1.3 - 04/12/2017
- fix overriding Django version by installing the package

## 0.1.2 - 04/12/2017
- remove support for Django 2.0

## 0.1.1 - 03/12/2017
- add parameters:
  * `app_names`
  * `--http-methods`
  * `--allow-status-code`
  * `--disallow-status-codes`
  * `--no-db`
- add setting `SKIP_SMOKE_TESTS`

[#2]: https://github.com/kamilkijak/django-smoke-tests/issues/2
[#5]: https://github.com/kamilkijak/django-smoke-tests/issues/5
[#15]: https://github.com/kamilkijak/django-smoke-tests/issues/15
[#17]: https://github.com/kamilkijak/django-smoke-tests/issues/17
