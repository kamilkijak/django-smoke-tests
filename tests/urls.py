# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_smoke_tests.urls import urlpatterns as django_smoke_tests_urls

urlpatterns = [
    url(r'^', include(django_smoke_tests_urls, namespace='django_smoke_tests')),
]
