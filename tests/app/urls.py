from django.urls import re_path

from .views import (
    app_view,
    skipped_app_view,
    view_with_decorator_with_wraps,
    view_with_decorator_without_wraps
)

# TODO: add tests using path()

url_patterns_with_decorator_with_wraps = [
    re_path(
        r'^decorator-with-wraps/$', view_with_decorator_with_wraps,
        name='decorator_with_wraps'
    ),
]

# views with custom decorators without @functools.wraps are not supported when specifying app_name
url_patterns_with_decorator_without_wraps = [
    re_path(
        r'^decorator-without-wraps/$', view_with_decorator_without_wraps,
        name='decorator_without_wraps'
    ),
]

skipped_app_url_patterns = [
    re_path(r'^skipped-app-endpoint/$', skipped_app_view, name='skipped_app_endpoint'),
]

urlpatterns = [
    re_path(r'^(/(?P<parameter>.+))?', app_view, name='app_view'),
] + url_patterns_with_decorator_with_wraps + url_patterns_with_decorator_without_wraps + \
    skipped_app_url_patterns
