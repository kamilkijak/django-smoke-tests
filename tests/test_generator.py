import random
import string
import unittest

from django.http import HttpResponse
from django.test import TestCase
try:
    from django.urls import RegexURLPattern
except ImportError:
    # Django < 1.10
    from django.core.urlresolvers import RegexURLPattern
from django.views.generic import RedirectView
from mock import patch
from parameterized import parameterized

from django_smoke_tests.generator import AppNotInInstalledApps, SmokeTestsGenerator
from django_smoke_tests.tests import SmokeTests

from tests.app.urls import urlpatterns as app_url_patterns
from tests.helpers import create_random_string
from tests.urls import url_patterns_with_authentication


# unpack to use in decorators
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
        url = '/simple-url'
        self.tests_generator.create_test_for_http_method(http_method, url, url)

        expected_test_name = self.tests_generator.create_test_name(http_method, url)
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
        endpoint_url = '/{}'.format(create_random_string())
        expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_url)

        self.tests_generator.create_test_for_http_method(
            http_method, endpoint_url, detail_url=True
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
            endpoint_url = '/{}'.format(create_random_string())
            expected_test_name = self.tests_generator.create_test_name(http_method, endpoint_url)

            self.tests_generator.create_test_for_http_method(
                http_method, endpoint_url
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
            endpoint_url = '/{}'.format(create_random_string())
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_url)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url
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
            endpoint_url = '/{}'.format(create_random_string())
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_url)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url
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
            endpoint_url = '/{}'.format(create_random_string())
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_url)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url
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
            endpoint_url = '/{}'.format(create_random_string())
            expected_test_name = tests_generator.create_test_name(http_method, endpoint_url)

            tests_generator.create_test_for_http_method(
                http_method, endpoint_url
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
    @patch('django_smoke_tests.generator.normalize')
    def test_create_skipped_test_for_not_supported_endpoint(self, http_method, mocked_normalize):
        mocked_normalize.return_value = []
        tests_generator = SmokeTestsGenerator()
        url_pattern = RegexURLPattern(
            r'^{}$'.format(create_random_string()),
            RedirectView.as_view(url='/', permanent=False),
            name=create_random_string()
        )
        expected_test_name = tests_generator.create_test_name(
            http_method, url_pattern.regex.pattern
        )

        tests_generator.create_tests_for_endpoint(
            url_pattern.regex.pattern, tests_generator.get_lookup_str(url_pattern)
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
            'GET', url_pattern_with_auth.regex.pattern
        )
        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)
        mocked_call_command.assert_called_once()
        self.assertTrue(is_successful)
        self.assertEqual(failures, [])
        self.assertEqual(tests_generator.warnings, [])

    def test_if_test_without_db_is_successful(self):
        tests_generator = SmokeTestsGenerator(use_db=False)
        http_method = 'GET'
        endpoint_url = '/{}'.format(create_random_string())
        expected_test_name = self.tests_generator.create_test_name(
            http_method, endpoint_url
        )
        tests_generator.create_test_for_http_method(
            http_method, endpoint_url
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

    @patch('django_smoke_tests.generator.call_command')
    def test_smoke_test_is_created_only_for_specified_app(
            self, mocked_call_command
    ):
        outside_app_url_pattern = RegexURLPattern(
            r'^{}$'.format(create_random_string()),
            RedirectView.as_view(url='/', permanent=False),
            name=create_random_string()
        )
        outside_app_test_name = self.tests_generator.create_test_name(
            'GET', outside_app_url_pattern.regex.pattern
        )

        inside_app_url_pattern = app_url_patterns[0]
        inside_app_url_full_pattern = '^app_urls/' + inside_app_url_pattern.regex.pattern
        inside_app_test_name = self.tests_generator.create_test_name(
            'GET', inside_app_url_full_pattern
        )

        tests_generator = SmokeTestsGenerator(app_name='tests.app')
        tests_generator.execute()

        self.assertFalse(
            hasattr(SmokeTests, outside_app_test_name)
        )

        self.assertTrue(
            hasattr(SmokeTests, inside_app_test_name)
        )

        mocked_call_command.assert_called_once_with('test', 'django_smoke_tests')

    @patch('django_smoke_tests.generator.call_command')
    def test_if_error_is_raised_when_app_is_not_in_installed_apps(self, mocked_call_command):
        with self.assertRaises(AppNotInInstalledApps):
            tests_generator = SmokeTestsGenerator(app_name=create_random_string())
            tests_generator.execute()
        mocked_call_command.assert_not_called()
