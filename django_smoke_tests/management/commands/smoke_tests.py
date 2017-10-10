from django.core.management import BaseCommand, call_command

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver

from ...tests import SmokeTests


def _test_generator(url, method, detail_url=False):
    def test(self):
        if method == 'GET':
            response = self.client.get(url)
        elif method == 'POST':
            response = self.client.post(url, {})
        elif method == 'DELETE':
            response = self.client.delete(url)

        allowed_status_codes = [200, 201, 301, 302, 304, 405]
        if detail_url:
            allowed_status_codes.append(404)
        self.assertIn(response.status_code, allowed_status_codes)
    return test


class Command(BaseCommand):
    help = "Smoke"

    METHODS_TO_TEST = ['GET', 'POST', 'DELETE']

    def handle(self, *args, **options):

        all_endpoints = get_resolver(None).reverse_dict

        for endpoint, endpoint_params in all_endpoints.items():
            if isinstance(endpoint, str):
                [(url_as_str, url_params)], url_pattern, _ = endpoint_params

                mocked_params = {param: 'random' for param in url_params}

                ready_url = url_as_str % mocked_params
                ready_url = ready_url if ready_url.startswith('/') else '/{}'.format(ready_url)
                self.create_tests_for_endpoint(ready_url, endpoint, detail_url=bool(url_params))

        call_command('test', 'django_smoke_tests')

    def create_tests_for_endpoint(self, url, endpoint, detail_url=False):
        for method in self.METHODS_TO_TEST:
            test = _test_generator(url, method, detail_url)
            setattr(SmokeTests, 'test_smoke_{}_{}'.format(method, endpoint), test)
