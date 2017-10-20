import random
from mock import patch

from django.test import TestCase

from django_smoke_tests.tests import SmokeTestsGenerator


class TestSmokeTestsGenerator(TestCase):

    def setUp(self):
        super(TestSmokeTestsGenerator, self).setUp()
        self.tests_generator = SmokeTestsGenerator()

    @patch('django_smoke_tests.tests.SmokeTests')
    def test_create_test_for_http_method(self, MockedSmokeTests):
        method = random.choice(self.tests_generator.SUPPORTED_HTTP_METHODS)
        endpoint_name = 'simple-endpoint'
        url = '/simple-url'
        self.tests_generator.create_test_for_http_method(method, url, endpoint_name)

        expected_test_name = self.tests_generator.create_test_name(method, endpoint_name)
        self.assertTrue(
            hasattr(MockedSmokeTests, expected_test_name)
        )
