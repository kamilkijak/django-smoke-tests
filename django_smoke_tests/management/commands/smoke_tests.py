from django.core.management import BaseCommand

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
        parser.add_argument(
            '--allowed-status-codes',
            default=None,
            type=str,
            help='Comma separated HTTP status codes that will be considered as success responses. '
                 'Eg. 200,201,204'
        )

    def handle(self, *args, **options):
        methods_to_test = self._get_list_from_string(options.get('http_methods'))
        allowed_status_codes = self._get_list_from_string(options.get('allowed_status_codes'))

        generator = SmokeTestsGenerator(
            http_methods=methods_to_test,
            allowed_status_codes=allowed_status_codes
        )
        generator.execute()

    @staticmethod
    def _get_list_from_string(option):
        return option.split(',') if option else None
