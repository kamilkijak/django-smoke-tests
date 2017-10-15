#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `smoke_tests` command.
"""
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

    @patch('django_smoke_tests.management.commands.smoke_tests.call_command')
    def test_proper_tests_were_created_for_default_methods(self, mocked_call_command):
        call_command('smoke_tests')
        mocked_call_command.assert_called()

        for url in urlpatterns:
            for method in self.command.METHODS_TO_TEST:
                test_name = self.command.create_test_name(method, url.name)
                self.assertTrue(hasattr(SmokeTests, test_name))

    def tearDown(self):
        pass
