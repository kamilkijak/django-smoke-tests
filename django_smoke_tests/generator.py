import random
import string

from django.core.management import call_command
from six import string_types

try:
    from django.urls import get_resolver
except ImportError:
    # Django < 1.10
    from django.core.urlresolvers import get_resolver
from unittest import skip

from django_smoke_tests.tests import SmokeTests


class HTTPMethodNotSupported(Exception):
    pass


class UrlStructureNotSupported(Exception):
    pass


class SmokeTestsGenerator:

    SUPPORTED_HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
    ALLOWED_STATUS_CODES = [200, 201, 301, 302, 304, 405]
    DISALLOWED_STATUS_CODES = [500, 501, 502]

    def __init__(self, http_methods=None, allowed_status_codes=None, disallowed_status_codes=None):
        if http_methods:
            self.validate_custom_http_methods(http_methods)
        self.methods_to_test = http_methods or self.SUPPORTED_HTTP_METHODS
        self.allowed_status_codes = allowed_status_codes
        self.disallowed_status_codes = disallowed_status_codes or self.DISALLOWED_STATUS_CODES
        self.warnings = []

    def validate_custom_http_methods(self, http_methods):
        unsupported_methods = set(http_methods) - set(self.SUPPORTED_HTTP_METHODS)
        if unsupported_methods:
            raise HTTPMethodNotSupported(
                'Methods {} are not supported'.format(list(unsupported_methods))
            )

    def _generate_test(self, url, method, detail_url=False):
        def test(self_of_test):
            http_method_function = getattr(self_of_test.client, method.lower(), None)
            response = http_method_function(url, {})
            additional_status_codes = [404] if detail_url else []
            if self.allowed_status_codes:
                self_of_test.assertIn(
                    response.status_code,
                    self.allowed_status_codes + additional_status_codes
                )
            else:
                self_of_test.assertNotIn(
                    response.status_code,
                    self.disallowed_status_codes
                )

        return test

    @staticmethod
    def _generate_skipped_test():
        @skip('Not supported')
        def test(self_of_test):
            pass
        return test

    def execute(self):
        all_endpoints = get_resolver(None).reverse_dict

        for endpoint, endpoint_params in all_endpoints.items():
            self.create_tests_for_endpoint(endpoint, endpoint_params)

        call_command('test', 'django_smoke_tests')

    def create_tests_for_endpoint(self, endpoint, endpoint_params):
        if isinstance(endpoint, string_types):
            try:
                url_as_str, url_params = self.strip_endpoint_params(endpoint_params)
            except UrlStructureNotSupported:
                self.warnings.append(
                    'Test skipped. URL << {} >> could not be stripped.'.format(
                        endpoint_params
                    ))
                self.create_tests_for_http_methods(None, None, skipped=True)
            else:
                fake_params = {param: self.create_random_string() for param in url_params}
                url = self.create_url(url_as_str, fake_params)
                self.create_tests_for_http_methods(url, endpoint, detail_url=bool(url_params))

    @staticmethod
    def strip_endpoint_params(endpoint_params):
        url_as_str, url_params = None, []

        try:
            [(url_as_str, url_params)], url_pattern, _ = endpoint_params
        except ValueError:
            # edge cases
            if len(endpoint_params[0]) > 1:
                [_, (url_as_str, url_params)], url_pattern, _ = endpoint_params

        if not url_as_str:
            raise UrlStructureNotSupported

        return url_as_str, url_params

    @staticmethod
    def create_random_string(length=5):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    @staticmethod
    def create_url(url_as_str, parameters):
        url = url_as_str % parameters
        return url if url.startswith('/') else '/{}'.format(url)

    def create_tests_for_http_methods(self, url, endpoint_name, detail_url=False, skipped=False):
        for method in self.methods_to_test:
            self.create_test_for_http_method(method, url, endpoint_name, detail_url, skipped)

    def create_test_for_http_method(
        self, method, url, endpoint_name, detail_url=False, skipped=False
    ):
        if skipped:
            test = self._generate_skipped_test()
        else:
            test = self._generate_test(url, method, detail_url)
        setattr(SmokeTests, self.create_test_name(method, endpoint_name), test)

    @staticmethod
    def create_test_name(method, endpoint_name):
        return 'test_smoke_{}_{}'.format(method, endpoint_name)
