from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class SmokeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        fixture_path = getattr(cls, 'fixture_path', None)
        if fixture_path:
            call_command('loaddata', fixture_path)

    @classmethod
    def setUpClass(cls):
        super(SmokeTests, cls).setUpClass()
        cls.smoke_user_credentials = {
            'username': 'smoke_superuser',
            'email': 'smoke@test.com',
            'password': 'smoke_password'
        }
        cls.smoke_user = get_user_model().objects.create_superuser(
            cls.smoke_user_credentials['username'],
            cls.smoke_user_credentials['email'],
            cls.smoke_user_credentials['password'],
        )

    def setUp(self):
        super(SmokeTests, self).setUp()
        try:
            self.client.force_login(self.smoke_user)  # faster than regular logging
        except AttributeError:
            # force_login available from Django 1.9
            self.client.login(
                usernme=self.smoke_user_credentials['username'],
                password=self.smoke_user_credentials['password']
            )

    def fail_test(self, url, http_method, response):
        fail_msg = (
            '\nSMOKE TEST FAILED'
            '\nURL: {}'
            '\nHTTP METHOD: {}'
            '\nSTATUS CODE: {}'
        ).format(url, http_method, response.status_code)
        self.fail(fail_msg)
