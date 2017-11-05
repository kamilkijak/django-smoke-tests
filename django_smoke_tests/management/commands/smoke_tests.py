from django.core.management import BaseCommand
from django.core.management.base import CommandError

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
            '--allow-status-codes',
            default=None,
            type=str,
            help='Comma separated HTTP status codes that will be considered as success responses. '
                 'Eg. 200,201,204'
        )
        parser.add_argument(
            '--disallow-status-codes',
            default=None,
            type=str,
            help='Comma separated HTTP status codes that will be considered as fail responses. '
                 'Eg. 404,500'
        )

    def handle(self, *args, **options):
        methods_to_test = self._get_list_from_string(options.get('http_methods'))
        allowed_status_codes = self._get_list_from_string(options.get('allow_status_codes'))
        disallowed_status_codes = self._get_list_from_string(options.get('disallow_status_codes'))

        if allowed_status_codes and disallowed_status_codes:
            raise CommandError(
                'You can either specify --allow-status-codes or --disallow-status-codes. '
                'You must not specify both.'
            )

        generator = SmokeTestsGenerator(
            http_methods=methods_to_test,
            allowed_status_codes=allowed_status_codes,
            disallowed_status_codes=disallowed_status_codes,
        )
        generator.execute()

        if generator.warnings:
            print(
                'Some tests were skipped. Please report on '
                'https://github.com/kamilkijak/django-smoke-tests/issues.'
            )
            print('\n'.join(generator.warnings))

    @staticmethod
    def _get_list_from_string(options):
        """
        Transforms comma separated string into a list of those elements.
        Transforms strings to ints if they are numbers.
        Eg.:
            "200,'400','xxx'" => [200, 400, 'xxx']
        """
        if options:
            return [
                int(option) if option.isdigit() else option for option in options.split(',')
            ]
        return None
