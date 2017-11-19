# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.views.generic import RedirectView

from .views import simple_method_view, view_with_django_auth, view_with_drf_auth, ViewWithDRFAuth


# kept separately, because they are used in tests
url_patterns_with_authentication = [
    url(r'^test-drf-auth/$', view_with_drf_auth, name='endpoint_with_drf_authentication'),
    url(
        r'^test-drf-auth-class/$', ViewWithDRFAuth.as_view(),
        name='endpoint_with_drf_authentication_class'
    ),
    url(r'^test-django-auth/$', view_with_django_auth, name='endpoint_with_django_authentication'),
]


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/', permanent=True), name='root_url'),
    url(r'^test/$', RedirectView.as_view(url='/', permanent=True), name='basic_endpoint'),
    url(r'^test-without-name/$', RedirectView.as_view(url='/', permanent=True)),
    url(
        r'^test-with-parameter/(?P<parameter>[0-9]+)$', simple_method_view,
        name='endpoint_with_parameter'
    ),

    # fixed edge cases
    url(r'^app_urls/', include('tests.app.urls')),

] + url_patterns_with_authentication
