from django.core.management import BaseCommand

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver

from ...tests import SmokeTestsGenerator


class Command(BaseCommand):
    help = "Smoke"

    def add_arguments(self, parser):
        parser.add_argument(
            '--http-methods',
            default=None,
            type=str,
            help='Comma separated HTTP methods that will be executed for all endpoint. '
                 'Eg. GET,POST,DELETE'
        )

    def handle(self, *args, **options):
        methods_to_test = options.get('http_methods')
        if methods_to_test:
            methods_to_test = methods_to_test.split(',')

        generator = SmokeTestsGenerator(methods_to_test=methods_to_test)
        generator.execute()
