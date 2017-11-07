import random
import unittest

from django.http import HttpResponse
from django.test import TestCase
from mock import patch
from parameterized import parameterized

from django_smoke_tests.generator import SmokeTestsGenerator
from django_smoke_tests.tests import SmokeTests


# unpack to use in decorators
from tests.urls import url_patterns_with_authentication

SUPPORTED_HTTP_METHODS = SmokeTestsGenerator.SUPPORTED_HTTP_METHODS
URL_PATTERNS_WITH_AUTH = [(url_pattern,) for url_pattern in url_patterns_with_authentication]


class DummyStream(object):
    """
    Mimics stream for tests executed withing another tests.
    Required for catching output of such tests, to not to show it in the console.
    """

    @staticmethod
    def write(*args, **kwargs):
        pass

    @staticmethod
    def flush():
        pass


class TestSmokeTestsGenerator(TestCase):
    def setUp(self):
        super(TestSmokeTestsGenerator, self).setUp()
        self.tests_generator = SmokeTestsGenerator()

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    @patch('django_smoke_tests.tests.SmokeTests')
    def test_create_test_for_http_method(self, http_method, MockedSmokeTests):
        endpoint_name = 'simple-endpoint'
        url = '/simple-url'
        self.tests_generator.create_test_for_http_method(http_method, url, endpoint_name)

        expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_name)
        self.assertTrue(
            hasattr(MockedSmokeTests, expected_test_name)
        )

    def _execute_smoke_test(self, test_name):
        """
        Executes one test inside current test suite.
        Be careful as it's kind on inception.
        """
        suite = unittest.TestSuite()
        suite.addTest(SmokeTests(test_name))
        test_runner = unittest.TextTestRunner(stream=DummyStream).run(suite)

        self.assertEqual(test_runner.errors, [])  # errors are never expected
        return test_runner.wasSuccessful(), test_runner.failures, test_runner.skipped

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_if_smoke_test_fails_on_allowed_response_status_code(self, http_method):
        # use new endpoint to be sure that test was not created in previous tests
        endpoint_name = self.tests_generator.create_random_string(length=10)
        endpoint_url = '/{}'.format(endpoint_name)
        expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_name)

        self.tests_generator.create_test_for_http_method(
            http_method, endpoint_url, endpoint_name, detail_url=True
        )  # detail_url set to True to allow 404

        # check if test was created and added to test class
        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )

        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)
        self.assertTrue(is_successful)
        self.assertEqual(failures, [])
        self.assertEqual(skipped, [])
        self.assertEqual(self.tests_generator.warnings, [])

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_if_smoke_test_fails_on_500_response_status_code(self, http_method):
        """
        Check if smoke test fails when gets 500 status code from endpoint's response.
        """
        with patch('django.test.client.Client.{}'.format(http_method.lower())) as mocked_method:
            mocked_method.return_value = HttpResponse(status=500)

            # use new endpoint to be sure that test was not created in previous tests
            endpoint_name = self.tests_generator.create_random_string(length=10)
            endpoint_url = '/{}'.format(endpoint_name)
            expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_name)

            self.tests_generator.create_test_for_http_method(
                http_method, endpoint_url, endpoint_name
            )

            # check if test was created and added to test class
            self.assertTrue(
                hasattr(SmokeTests, expected_test_name)
            )

            is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

            self.assertFalse(is_successful)
            self.assertEqual(len(failures), 1)
            self.assertEqual(skipped, [])
            self.assertEqual(self.tests_generator.warnings, [])

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_if_smoke_test_passes_on_custom_allowed_response_status_codes(self, http_method):
        random_status_code = random.randint(100, 510)
        custom_allowed_status_codes = [random_status_code, random_status_code + 1]
        tests_generator = SmokeTestsGenerator(allowed_status_codes=custom_allowed_status_codes)

        with patch('django.test.client.Client.{}'.format(http_method.lower())) as mocked_method:
            mocked_method.return_value = HttpResponse(status=custom_allowed_status_codes[0])

            # use new endpoint to be sure that test was not created in previous tests
            endpoint_name = tests_generator.create_random_string(length=10)
            endpoint_url = '/{}'.format(endpoint_name)
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_name)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url, endpoint_name
            )

            # check if test was created and added to test class
            self.assertTrue(
                hasattr(SmokeTests, expected_test_name)
            )

            is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

            self.assertTrue(is_successful)
            self.assertEqual(failures, [])
            self.assertEqual(skipped, [])
            self.assertEqual(tests_generator.warnings, [])

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_if_smoke_test_fails_on_custom_allowed_response_status_codes(self, http_method):
        random_status_code = random.randint(100, 510)
        custom_allowed_status_codes = [random_status_code, random_status_code + 1]
        tests_generator = SmokeTestsGenerator(allowed_status_codes=custom_allowed_status_codes)

        with patch('django.test.client.Client.{}'.format(http_method.lower())) as mocked_method:
            # return different status code
            mocked_method.return_value = HttpResponse(status=custom_allowed_status_codes[0] + 10)

            # use new endpoint to be sure that test was not created in previous tests
            endpoint_name = tests_generator.create_random_string(length=10)
            endpoint_url = '/{}'.format(endpoint_name)
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_name)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url, endpoint_name
            )

            # check if test was created and added to test class
            self.assertTrue(
                hasattr(SmokeTests, expected_test_name)
            )

            is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

            self.assertFalse(is_successful)
            self.assertEqual(len(failures), 1)
            self.assertEqual(skipped, [])
            self.assertEqual(tests_generator.warnings, [])

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_if_smoke_test_passes_on_custom_disallowed_response_status_codes(self, http_method):
        random_status_code = random.randint(100, 510)
        custom_disallowed_status_codes = [random_status_code, random_status_code + 1]
        tests_generator = SmokeTestsGenerator(
            disallowed_status_codes=custom_disallowed_status_codes
        )

        with patch('django.test.client.Client.{}'.format(http_method.lower())) as mocked_method:
            # return different status code than disallowed
            mocked_method.return_value = HttpResponse(status=random_status_code + 10)

            # use new endpoint to be sure that test was not created in previous tests
            endpoint_name = tests_generator.create_random_string(length=10)
            endpoint_url = '/{}'.format(endpoint_name)
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_name)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url, endpoint_name
            )

            # check if test was created and added to test class
            self.assertTrue(
                hasattr(SmokeTests, expected_test_name)
            )

            is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

            self.assertTrue(is_successful)
            self.assertEqual(failures, [])
            self.assertEqual(tests_generator.warnings, [])

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_if_smoke_test_fails_on_custom_disallowed_response_status_codes(self, http_method):
        random_status_code = random.randint(100, 510)
        custom_disallowed_status_codes = [random_status_code, random_status_code + 1]
        tests_generator = SmokeTestsGenerator(
            disallowed_status_codes=custom_disallowed_status_codes
        )

        with patch('django.test.client.Client.{}'.format(http_method.lower())) as mocked_method:
            # return different status code than disallowed
            mocked_method.return_value = HttpResponse(status=custom_disallowed_status_codes[0])

            # use new endpoint to be sure that test was not created in previous tests
            endpoint_name = tests_generator.create_random_string(length=10)
            endpoint_url = '/{}'.format(endpoint_name)
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_name)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url, endpoint_name
            )

            # check if test was created and added to test class
            self.assertTrue(
                hasattr(SmokeTests, expected_test_name)
            )
            is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

            self.assertFalse(is_successful)
            self.assertEqual(len(failures), 1)
            self.assertEqual(skipped, [])
            self.assertEqual(tests_generator.warnings, [])

    @parameterized.expand(SUPPORTED_HTTP_METHODS)
    def test_create_skipped_test_for_not_supported_endpoint(self, http_method):
        tests_generator = SmokeTestsGenerator()

        endpoint_name = tests_generator.create_random_string(length=10)
        endpoint_params = ((), ())  # empty tuples not supported
        expected_test_name = tests_generator.create_test_name(http_method, endpoint_name)

        tests_generator.create_tests_for_endpoint(
            endpoint_name, endpoint_params
        )
        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )

        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

        self.assertEqual(len(skipped), 1)
        self.assertEqual(len(tests_generator.warnings), 1)

    @parameterized.expand(URL_PATTERNS_WITH_AUTH)
    @patch('django_smoke_tests.generator.call_command')
    def test_if_authentication_is_successful(self, url_pattern_with_auth, mocked_call_command):
        tests_generator = SmokeTestsGenerator()
        tests_generator.execute()
        expected_test_name = self.tests_generator.create_test_name(
            'GET', url_pattern_with_auth.name
        )
        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)
        mocked_call_command.assert_called_once()
        self.assertTrue(is_successful)
        self.assertEqual(failures, [])
        self.assertEqual(tests_generator.warnings, [])

    def test_if_test_without_db_is_successful(self):
        tests_generator = SmokeTestsGenerator(use_db=False)
        http_method = 'GET'
        endpoint_name = self.tests_generator.create_random_string(length=10)
        endpoint_url = '/{}'.format(endpoint_name)
        expected_test_name = self.tests_generator.create_test_name(
            http_method, endpoint_name
        )
        tests_generator.create_test_for_http_method(
            http_method, endpoint_url, endpoint_name
        )
        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)
        self.assertTrue(is_successful)
        self.assertEqual(failures, [])
        self.assertEqual(tests_generator.warnings, [])

    @patch('django_smoke_tests.generator.call_command')
    def test_if_test_without_db_is_called_with_custom_runner(self, mocked_call_command):
        tests_generator = SmokeTestsGenerator(use_db=False)
        tests_generator.execute()
        mocked_call_command.assert_called_once_with(
            'test', 'django_smoke_tests', testrunner='django_smoke_tests.runners.NoDbTestRunner'
        )
