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

Documentation
-------------

The full documentation is at https://django-smoke-tests.readthedocs.io.

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

Features
--------

* TODO

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
