# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.views.generic import RedirectView

from .views import test_view


urlpatterns = [
    url(r'$', RedirectView.as_view(url='/', permanent=True), name='root_url'),
    url(r'^test/', RedirectView.as_view(url='/', permanent=True), name='basic_endpoint'),
    url(r'^test-with-parameter/(?P<parameter>[0-9]+)$', test_view, name='endpoint_with_parameter'),

    # fixed edge cases
    url(r'^app_urls/', include('tests.app.urls')),
]
