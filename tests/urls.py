# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.urls import path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from .views import (
    skipped_view, simple_method_view, view_with_django_auth, view_with_drf_auth, SimpleViewSet,
    ViewWithDRFAuth
)


# kept separately, because they are used in tests
url_patterns_with_authentication = [
    url(r'^test-drf-auth/$', view_with_drf_auth, name='endpoint_with_drf_authentication'),
    url(
        r'^test-drf-auth-class/$', ViewWithDRFAuth.as_view(),
        name='endpoint_with_drf_authentication_class'
    ),
    url(r'^test-django-auth/$', view_with_django_auth, name='endpoint_with_django_authentication'),
]

skipped_url_patterns = [
    url(r'^skipped-endpoint/$', skipped_view, name='skipped_endpoint'),
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
    path('app_urls/', include('tests.app.urls')),
    path('another_app_urls/', include('tests.another_app.urls', namespace='another_app_namespace')),

    # using path()
    path(
      'test-with-new-style-parameter/<int:parameter>', simple_method_view,
      name='endpoint_with_new_style_parameter'
    ),

    path('admin/users/<str:parameter>/delete/', simple_method_view, name='delete_user')

] + url_patterns_with_authentication + skipped_url_patterns

router = DefaultRouter()
router.register(r'view-set', SimpleViewSet, basename='view-set')

urlpatterns += router.urls
