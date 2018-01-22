==================
django-smoke-tests
==================

.. image:: https://badge.fury.io/py/django-smoke-tests.svg
    :target: https://badge.fury.io/py/django-smoke-tests

.. image:: https://travis-ci.org/kamilkijak/django-smoke-tests.svg?branch=master
    :target: https://travis-ci.org/kamilkijak/django-smoke-tests

.. image:: https://codecov.io/gh/kamilkijak/django-smoke-tests/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/kamilkijak/django-smoke-tests

Django command that finds all endpoints in project, executes HTTP requests against them and checks if there are any unexpected responses.

.. image:: https://i.imgur.com/cPK0y3W.gif

.. _contents:

.. contents::

Requirements
------------

- Python (2.7, 3.4, 3.5, 3.6)
- Django (1.8, 1.9, 1.10, 1.11, 2.0)

Installation
------------
Install using pip::

    pip install django-smoke-tests


Add it to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_smoke_tests',
        ...
    )


Quickstart
----------
Execute smoke tests for the whole project::

    python manage.py smoke_tests


Usage
-----

Parameters
~~~~~~~~~~
::

    $ python manage.py smoke_tests --help
    usage: manage.py smoke_tests [-h] [--http-methods HTTP_METHODS]
                                 [--allow-status-codes ALLOW_STATUS_CODES]
                                 [--disallow-status-codes DISALLOW_STATUS_CODES]
                                 [--settings SETTINGS]
                                 [--configuration CONFIGURATION]
                                 [--fixture FIXTURE] [--no-migrations] [--no-db]
                                 [app_names]

    Smoke tests for Django endpoints.

    positional arguments:
      app_names             names of apps to test

    optional arguments:
      -h, --help            show this help message and exit
      --http-methods HTTP_METHODS
                            comma separated HTTP methods that will be executed for
                            all endpoints, eg. GET,POST,DELETE
                            [default: GET,POST,PUT,DELETE]
      -g, --get-only        shortcut for --http-methods GET
      --allow-status-codes ALLOW_STATUS_CODES
                            comma separated HTTP status codes that will be
                            considered as success responses, eg. 200,201,204
                            [default: 200,201,301,302,304,405]
      --disallow-status-codes DISALLOW_STATUS_CODES
                            comma separated HTTP status codes that will be
                            considered as fail responses, eg. 404,500
      --settings SETTINGS   path to the Django settings module, eg.
                            myproject.settings
      --configuration CONFIGURATION
                            name of the configuration class to load, eg.
                            Development
      --fixture FIXTURE     Django fixture JSON file to be loaded before executing
                            smoke tests
      --no-migrations       flag for skipping migrations, database will be created
                            directly from models
      --no-db               flag for skipping database creation


Skipping tests
~~~~~~~~~~~~~~
To skip tests for specific URLs add ``SKIP_SMOKE_TESTS`` option in your settings.

This setting should contain list of URLs' names.

.. code-block:: python

    SKIP_SMOKE_TESTS = (
        'all-astronauts',  # to skip url(r'^astronauts/', AllAstronauts.as_view(), name='all-astronauts')
    )


Reporting bugs
--------------
If you face any problems please report them to the issue tracker at https://github.com/kamilkijak/django-smoke-tests/issues

Contributing
-------------

Running Tests
~~~~~~~~~~~~~~
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
