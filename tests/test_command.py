#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `smoke_tests` command.
"""
import random

from django.core.management import call_command
from django.test import TestCase
from mock import patch

from django_smoke_tests.tests import SmokeTests
from django_smoke_tests.management.commands import smoke_tests
from .urls import urlpatterns


class TestSmokeTestsCommand(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSmokeTestsCommand, cls).setUpClass()
        cls.command = smoke_tests.Command()
        cls.all_possible_methods = ['GET', 'HEAD', 'PUT', 'PATCH', 'POST', 'DELETE']

    @patch('django_smoke_tests.management.commands.smoke_tests.call_command')
    def test_proper_tests_were_created_for_default_methods(self, mocked_call_command):
        call_command('smoke_tests')
        mocked_call_command.assert_called()

        for url in urlpatterns:
            for method in self.command.METHODS_TO_TEST:
                test_name = self.command.create_test_name(method, url.name)
                self.assertTrue(hasattr(SmokeTests, test_name))

    @patch('django_smoke_tests.management.commands.smoke_tests.call_command')
    def test_only_proper_tests_were_created_for_custom_methods(self, mocked_call_command):
        shuffled_methods = random.sample(self.all_possible_methods, len(self.all_possible_methods))
        split_index = random.randint(1, len(shuffled_methods) - 1)
        methods_to_call = shuffled_methods[:split_index]
        methods_not_called = shuffled_methods[split_index:]

        call_command('smoke_tests', http_methods=','.join(methods_to_call))
        mocked_call_command.assert_called()

        for url in urlpatterns:
            for method in methods_to_call:
                test_name = self.command.create_test_name(method, url.name)
                self.assertTrue(hasattr(SmokeTests, test_name))

            for method in methods_not_called:
                test_name = self.command.create_test_name(method, url.name)
                self.assertFalse(hasattr(SmokeTests, test_name))

    def tearDown(self):
        pass
