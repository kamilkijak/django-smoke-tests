from django.contrib.auth.models import User
from django.test import TestCase


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
