import random
import string

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import get_resolver


class SmokeTestsGenerator:

    METHODS_TO_TEST = ['GET', 'POST', 'DELETE']

    def __init__(self, methods_to_test=None):
        self.methods_to_test = methods_to_test or self.METHODS_TO_TEST

    @staticmethod
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

    def execute(self):
        all_endpoints = get_resolver(None).reverse_dict

        for endpoint, endpoint_params in all_endpoints.items():
            self.create_tests_for_endpoint(endpoint, endpoint_params)

        call_command('test', 'django_smoke_tests')

    def create_tests_for_endpoint(self, endpoint, endpoint_params):
        if isinstance(endpoint, str):
            [(url_as_str, url_params)], url_pattern, _ = endpoint_params

            fake_params = {param: self.create_random_string() for param in url_params}
            url = self.create_url(url_as_str, fake_params)
            self.create_tests_for_http_methods(url, endpoint, detail_url=bool(url_params))

    @staticmethod
    def create_random_string(length=5):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    @staticmethod
    def create_url(url_as_str, parameters):
        url = url_as_str % parameters
        return url if url.startswith('/') else '/{}'.format(url)

    def create_tests_for_http_methods(self, url, endpoint_name, detail_url=False):
        for method in self.methods_to_test:
            test = self._test_generator(url, method, detail_url)
            setattr(SmokeTests, self.create_test_name(method, endpoint_name), test)

    @staticmethod
    def create_test_name(method, endpoint_name):
        return 'test_smoke_{}_{}'.format(method, endpoint_name)


class SmokeTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super(SmokeTests, cls).setUpClass()

        smoke_user_credentials = {
            'username': 'smoke_superuser3',
            'email': 'smoke@test.com',
            'password': 'smoke_password'
        }
        smoke_user = User.objects.create_superuser(
            smoke_user_credentials['username'],
            smoke_user_credentials['email'],
            smoke_user_credentials['password'],
        )
