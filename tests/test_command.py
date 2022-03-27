#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `smoke_tests` command.
"""
import random

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.urls import URLPattern
from mock import patch

from django_smoke_tests.generator import HTTPMethodNotSupported, SmokeTestsGenerator, get_pattern
from django_smoke_tests.tests import SmokeTests
from .urls import urlpatterns
from .helpers import captured_output, create_random_string


class TestSmokeTestsCommand(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSmokeTestsCommand, cls).setUpClass()
        cls.test_generator = SmokeTestsGenerator()
        cls.all_possible_methods = cls.test_generator.SUPPORTED_HTTP_METHODS

    @patch('django_smoke_tests.generator.call_command')
    def test_proper_tests_were_created_for_default_methods(self, mocked_call_command):
        call_command('smoke_tests')
        mocked_call_command.assert_called_once()

        # skip RegexURLResolver (eg. include(app.urls))
        urlpatterns_without_resolvers = [
            url for url in urlpatterns if isinstance(url, URLPattern)
        ]

        for url in urlpatterns_without_resolvers:
            for method in self.test_generator.SUPPORTED_HTTP_METHODS:
                test_name = self.test_generator.create_test_name(method, get_pattern(url))
                self.assertTrue(hasattr(SmokeTests, test_name))

    @patch('django_smoke_tests.generator.call_command')
    def test_only_proper_tests_were_created_for_custom_methods(self, mocked_call_command):
        shuffled_methods = random.sample(self.all_possible_methods, len(self.all_possible_methods))
        split_index = random.randint(1, len(shuffled_methods) - 1)
        methods_to_call = shuffled_methods[:split_index]
        methods_not_called = shuffled_methods[split_index:]

        call_command('smoke_tests', http_methods=','.join(methods_to_call))
        mocked_call_command.assert_called_once()

        # skip RegexURLResolver (eg. include(app.urls))
        urlpatterns_without_resolvers = [
            url for url in urlpatterns if isinstance(url, URLPattern)
        ]

        for url in urlpatterns_without_resolvers:
            for method in methods_to_call:
                test_name = self.test_generator.create_test_name(method, get_pattern(url))
                self.assertTrue(hasattr(SmokeTests, test_name))

            for method in methods_not_called:
                test_name = self.test_generator.create_test_name(method, get_pattern(url))
                self.assertFalse(hasattr(SmokeTests, test_name))

    @patch('django_smoke_tests.generator.call_command')
    def test_raise_an_error_for_not_supported_http_method(self, mocked_call_command):
        with self.assertRaises(HTTPMethodNotSupported):
            call_command('smoke_tests', http_methods='WRONG')
        mocked_call_command.assert_not_called()

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_right_allowed_status_codes_are_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        allowed_status_codes = '200,201'
        call_command('smoke_tests', allow_status_codes=allowed_status_codes)
        self.assertEqual(
            mocked_generator.call_args[1]['allowed_status_codes'],
            [int(code) for code in allowed_status_codes.split(',')]
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_right_disallowed_status_codes_are_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        disallowed_status_codes = '400,401'
        call_command('smoke_tests', disallow_status_codes=disallowed_status_codes)
        self.assertEqual(
            mocked_generator.call_args[1]['disallowed_status_codes'],
            [int(code) for code in disallowed_status_codes.split(',')]
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_disable_migrations_option_is_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        disable_migrations = True

        call_command('smoke_tests', no_migrations=disable_migrations)
        self.assertEqual(
            mocked_generator.call_args[1]['disable_migrations'],
            disable_migrations
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_use_db_option_is_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        no_db = True

        call_command('smoke_tests', no_db=no_db)
        self.assertEqual(
            mocked_generator.call_args[1]['use_db'],
            not no_db
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_app_name_option_is_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        app_name = 'test_app_name'

        call_command('smoke_tests', app_name)
        self.assertEqual(
            mocked_generator.call_args[1]['app_names'][0],
            app_name
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_multiple_app_names_are_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        first_app = create_random_string()
        second_app = create_random_string()

        call_command('smoke_tests', ','.join([first_app, second_app]))
        self.assertEqual(
            mocked_generator.call_args[1]['app_names'][0],
            first_app
        )
        self.assertEqual(
            mocked_generator.call_args[1]['app_names'][1],
            second_app
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_settings_option_is_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        settings = 'tests.settings'

        call_command('smoke_tests', settings=settings)
        self.assertEqual(
            mocked_generator.call_args[1]['settings_module'],
            settings
        )

    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_configuration_option_is_passed_to_test_generator(self, mocked_generator):
        mocked_generator.return_value.warnings = []
        configuration = 'Development'

        call_command('smoke_tests', configuration=configuration)
        self.assertEqual(
            mocked_generator.call_args[1]['configuration'],
            configuration
        )

    def test_error_is_raised_when_both_allowed_and_disallowed_specified(self):
        allowed_status_codes = '200,201'
        disallowed_status_codes = '400,401'

        with self.assertRaises(CommandError):
            call_command(
                'smoke_tests',
                allow_status_codes=allowed_status_codes,
                disallow_status_codes=disallowed_status_codes
            )

    @patch('django_smoke_tests.generator.call_command')
    @patch('django_smoke_tests.management.commands.smoke_tests.SmokeTestsGenerator')
    def test_warnings_are_printed(self, mocked_generator, mocked_call_command):
        mocked_generator.return_value.warnings = [
            create_random_string() for _ in range(random.randint(1, 10))
        ]

        with captured_output() as (out, err):
            call_command('smoke_tests')

        self.assertNotEqual(out.getvalue(), '')
        mocked_call_command.assert_not_called()
