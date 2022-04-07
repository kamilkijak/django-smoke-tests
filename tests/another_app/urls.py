from django.urls import path

from .views import dummy_view


app_name = 'another_app'
another_app_skipped_urls = [
    path('skipped-app-endpoint-by-namespace/', dummy_view, name='skipped_endpoint_by_namespace_in_another_app'),
    path('skipped-app-endpoint-by-app-name/', dummy_view, name='skipped_endpoint_by_app_name_in_another_app'),
]

urlpatterns = another_app_skipped_urls