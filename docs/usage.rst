=====
Usage
=====

To use django-smoke-tests in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_smoke_tests.apps.DjangoSmokeTestsConfig',
        ...
    )

Add django-smoke-tests's URL patterns:

.. code-block:: python

    from django_smoke_tests import urls as django_smoke_tests_urls


    urlpatterns = [
        ...
        url(r'^', include(django_smoke_tests_urls)),
        ...
    ]
