from django.core.management import BaseCommand

try:
    from django.urls import get_resolver
except ImportError:
    # Django < 1.10
    from django.core.urlresolvers import get_resolver

from ...generator import SmokeTestsGenerator


class Command(BaseCommand):
    help = "Smoke tests for Django endpoints."

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

        generator = SmokeTestsGenerator(http_methods=methods_to_test)
        generator.execute()
