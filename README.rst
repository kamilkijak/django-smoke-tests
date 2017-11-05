=============================
django-smoke-tests
=============================

.. image:: https://badge.fury.io/py/django-smoke-tests.svg
    :target: https://badge.fury.io/py/django-smoke-tests

.. image:: https://travis-ci.org/kamilkijak/django-smoke-tests.svg?branch=master
    :target: https://travis-ci.org/kamilkijak/django-smoke-tests

.. image:: https://codecov.io/gh/kamilkijak/django-smoke-tests/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/kamilkijak/django-smoke-tests

Smoke tests for Django project.

Quickstart
----------

Install django-smoke-tests::

    pip install django-smoke-tests

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_smoke_tests',
        ...
    )

Execute smoke tests::

    python manage.py smoke_tests


Documentation
-------------

Parameters
~~~~~~~~~~
+-------------------------+-----------------------------------------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------+
| Parameter               | Example                                                   | Default                 | Description                                                                                                    |
+-------------------------+-----------------------------------------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------+
| --http-methods          | python manage.py smoke_tests --http-methods=GET,POST      | GET,POST,PUT,DELETE     | Comma separated list of HTTP methods that will be executed for each endpoint.                                  |
+-------------------------+-----------------------------------------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------+
| --allow-status-codes    | python manage.py smoke_tests --allow-status-codes=200,201 | 200,201,301,302,304,405 | Comma separated list of response status codes that will be considered as successful tests (expected response). |
+-------------------------+-----------------------------------------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------+
| --disallow-status-codes | python manage.py smoke_tests --disallow-status-codes=500  | 500,501,502             | Comma separated list of response status codes that will be considered as failed tests (expected response).     |
+-------------------------+-----------------------------------------------------------+-------------------------+----------------------------------------------------------------------------------------------------------------+

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
