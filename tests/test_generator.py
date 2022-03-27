import random
import unittest

from django.http import HttpResponse
from django.test import TestCase, override_settings

from django_smoke_tests.migrations import DisableMigrations

from django.urls import URLPattern
from django.views.generic import RedirectView
from mock import patch
from parameterized import parameterized

from django_smoke_tests.generator import AppNotInInstalledApps, SmokeTestsGenerator, get_pattern
from django_smoke_tests.runners import NoDbTestRunner
from django_smoke_tests.tests import SmokeTests

from tests.app.urls import urlpatterns as app_url_patterns
from tests.app.urls import skipped_app_url_patterns
from tests.app.urls import (
    url_patterns_with_decorator_with_wraps, url_patterns_with_decorator_without_wraps
)
from tests.helpers import captured_output, create_random_string
from tests.urls import url_patterns_with_authentication, skipped_url_patterns


SKIPPED_URL_PATTERNS = skipped_url_patterns + skipped_app_url_patterns

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

    def tearDown(self):
        # remove all tests created and added to SmokeTests
        tests_created = [attr for attr in vars(SmokeTests) if attr.startswith('test_smoke')]
        for test_name in tests_created:
            delattr(SmokeTests, test_name)

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
        url_pattern = URLPattern(
            r'^{}$'.format(create_random_string()),
            RedirectView.as_view(url='/', permanent=False),
            name=create_random_string()
        )
        expected_test_name = tests_generator.create_test_name(
            http_method, get_pattern(url_pattern)
        )

        tests_generator.create_tests_for_endpoint(
            get_pattern(url_pattern), url_pattern.name
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
            'GET', get_pattern(url_pattern_with_auth)
        )
        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)
        mocked_call_command.assert_called_once()
        self.assertTrue(is_successful)
        self.assertEqual(failures, [])
        self.assertEqual(tests_generator.warnings, [])

    @override_settings(MIGRATION_MODULES=DisableMigrations())
    def test_if_test_with_disabled_migrations_is_successful(self):
        tests_generator = SmokeTestsGenerator()
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
    @patch('django_smoke_tests.generator.settings')
    def test_if_disable_migrations_option_is_applied(self, mocked_settings, mocked_call_command):
        tests_generator = SmokeTestsGenerator(disable_migrations=True)
        tests_generator.execute()
        self.assertTrue(isinstance(mocked_settings.MIGRATION_MODULES, DisableMigrations))

    @patch('django_smoke_tests.generator.call_command')
    def test_if_settings_module_option_is_applied(self, mocked_call_command):
        settings_module = 'tests.settings'
        tests_generator = SmokeTestsGenerator(settings_module=settings_module)
        tests_generator.execute()
        mocked_call_command.assert_called_once_with(
            'test', 'django_smoke_tests', settings=settings_module
        )

    @patch('django_smoke_tests.generator.call_command')
    def test_if_configuration_option_is_applied(self, mocked_call_command):
        configuration = 'Development'
        tests_generator = SmokeTestsGenerator(configuration=configuration)
        tests_generator.execute()
        mocked_call_command.assert_called_once_with(
            'test', 'django_smoke_tests', configuration=configuration
        )

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

    def test_no_db_test_runner(self):
        tests_generator = SmokeTestsGenerator(use_db=False)
        http_method = 'GET'
        endpoint_url = '/{}'.format(create_random_string())
        expected_test_name = self.tests_generator.create_test_name(
            http_method, endpoint_url
        )
        tests_generator.create_test_for_http_method(
            http_method, endpoint_url
        )
        suite = unittest.TestSuite()
        suite.addTest(SmokeTests(expected_test_name))
        with captured_output() as (_, _):  # skip output
            test_runner = NoDbTestRunner(stream=DummyStream, verbosity=-1).run_suite(suite)

        self.assertEqual(test_runner.errors, [])
        self.assertTrue(test_runner.wasSuccessful())
        self.assertEqual(test_runner.failures, [])
        self.assertEqual(test_runner.skipped, [])

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
        outside_app_url_pattern = URLPattern(
            r'^{}$'.format(create_random_string()),
            RedirectView.as_view(url='/', permanent=False),
            name=create_random_string()
        )
        outside_app_test_name = self.tests_generator.create_test_name(
            'GET', get_pattern(outside_app_url_pattern)
        )

        inside_app_url_pattern = app_url_patterns[0]
        inside_app_url_full_pattern = '^app_urls/' + get_pattern(inside_app_url_pattern)
        inside_app_test_name = self.tests_generator.create_test_name(
            'GET', inside_app_url_full_pattern
        )

        tests_generator = SmokeTestsGenerator(app_names=['tests.app'])
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
            tests_generator = SmokeTestsGenerator(app_names=[create_random_string()])
            tests_generator.execute()
        mocked_call_command.assert_not_called()

    @patch('django_smoke_tests.generator.call_command')
    def test_if_view_decorated_with_wraps_is_added_for_specified_app(self, mocked_call_command):
        url_pattern = url_patterns_with_decorator_with_wraps[0]
        http_method = 'GET'
        tests_generator = SmokeTestsGenerator(app_names=['tests.app'], http_methods=[http_method])
        tests_generator.execute()

        expected_test_name = self.tests_generator.create_test_name(
            http_method, '^app_urls/' + get_pattern(url_pattern)
        )
        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )
        mocked_call_command.assert_called_once()

    @patch('django_smoke_tests.generator.call_command')
    def test_if_view_decorated_without_wraps_is_not_added_for_specified_app(
            self, mocked_call_command
    ):
        # it's not possible to retrieve callback (view) module when it's wrapped in decorator
        url_pattern = url_patterns_with_decorator_without_wraps[0]
        http_method = 'GET'
        tests_generator = SmokeTestsGenerator(app_names=['tests.app'], http_methods=[http_method])
        tests_generator.execute()

        expected_test_name = self.tests_generator.create_test_name(
            http_method, '^app_urls/' + get_pattern(url_pattern)
        )
        self.assertFalse(
            hasattr(SmokeTests, expected_test_name)
        )
        mocked_call_command.assert_called_once()

    @patch('django_smoke_tests.generator.call_command')
    def test_skipped_url(self, mocked_call_command):
        url_pattern = skipped_url_patterns[0]
        http_method = 'GET'
        tests_generator = SmokeTestsGenerator(http_methods=[http_method])
        tests_generator.execute()

        expected_test_name = tests_generator.create_test_name(
            http_method, get_pattern(url_pattern)
        )

        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )

        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

        self.assertTrue(is_successful)
        self.assertEqual(len(skipped), 1)
        self.assertEqual(failures, [])

    @patch('django_smoke_tests.generator.call_command')
    def test_skipped_app_url(self, mocked_call_command):
        url_pattern = skipped_app_url_patterns[0]
        http_method = 'GET'
        tests_generator = SmokeTestsGenerator(http_methods=[http_method])
        tests_generator.execute()

        expected_test_name = tests_generator.create_test_name(
            http_method, '^app_urls/' + get_pattern(url_pattern)
        )

        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )

        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

        self.assertTrue(is_successful)
        self.assertEqual(len(skipped), 1)
        self.assertEqual(failures, [])

    @override_settings(SKIP_SMOKE_TESTS=())
    @patch('django_smoke_tests.generator.call_command')
    def test_if_url_is_not_skipped_when_setting_is_empty(self, mocked_call_command):
        url_pattern = skipped_url_patterns[0]
        http_method = 'GET'
        tests_generator = SmokeTestsGenerator(http_methods=[http_method])
        tests_generator.execute()

        expected_test_name = tests_generator.create_test_name(
            http_method, get_pattern(url_pattern)
        )

        self.assertTrue(
            hasattr(SmokeTests, expected_test_name)
        )

        is_successful, failures, skipped = self._execute_smoke_test(expected_test_name)

        self.assertTrue(is_successful)
        self.assertEqual(skipped, [])
        self.assertEqual(failures, [])

    @patch('django_smoke_tests.tests.call_command')
    @patch('django_smoke_tests.generator.call_command')
    def test_if_fixture_is_applied(self, call_command_for_test, call_command_for_loaddata):
        fixture_path = 'file.json'
        tests_generator = SmokeTestsGenerator(fixture_path=fixture_path)
        tests_generator.execute()

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
        self.assertEqual(skipped, [])
        self.assertEqual(failures, [])

        call_command_for_test.assert_called_once_with(
            'test', 'django_smoke_tests'
        )
        call_command_for_loaddata.assert_called_once_with(
            'loaddata', fixture_path
        )
