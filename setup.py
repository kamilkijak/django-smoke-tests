#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from django_smoke_tests/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("django_smoke_tests", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()

_read = lambda f: open(
    os.path.join(os.path.dirname(__file__), f)).read() if os.path.exists(f) else ''

install_requires = [
    l.replace('==', '>=') for l in _read('requirements.txt').split('\n')
    if l and not l.startswith('#') and not l.startswith('-')]

setup(
    name='django-smoke-tests',
    version=version,
    description="""Smoke tests for Django project.""",
    long_description=readme,
    author='Kamil Kijak',
    author_email='kamilkijak@gmail.com',
    url='https://github.com/kamilkijak/django-smoke-tests',
    packages=[
        'django_smoke_tests',
    ],
    include_package_data=True,
    install_requires=install_requires,
    license="MIT",
    zip_safe=False,
    keywords=['django-smoke-tests', 'test', 'smoke'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
