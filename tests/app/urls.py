from django.conf.urls import url

from .views import app_view


urlpatterns = [
    url(r'^(/(?P<parameter>.+))?', app_view, name='app_view'),
]
