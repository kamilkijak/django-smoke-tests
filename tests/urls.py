# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^test/', RedirectView.as_view(url='/', permanent=True), name='test_endpoint'),
]
