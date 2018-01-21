import argparse
import os

from django.core.management import BaseCommand, CommandParser
from django.core.management.base import CommandError

from ...generator import SmokeTestsGenerator


class Command(BaseCommand):
    help = "Smoke tests for Django endpoints."

    def create_parser(self, prog_name, subcommand):
        """
        Override in order to skip default parameters like verbosity, version, etc.
        """
        parser = CommandParser(
            self, prog="%s %s" % (os.path.basename(prog_name), subcommand),
            description=self.help or None,
        )
        # create hidden options (required by BaseCommand)
        parser.add_argument('--no-color', help=argparse.SUPPRESS)
        parser.add_argument('--pythonpath', help=argparse.SUPPRESS)
        parser.add_argument('--traceback', help=argparse.SUPPRESS)
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        methods_group = parser.add_mutually_exclusive_group()
        methods_group.add_argument(
            '--http-methods',
            default=None,
            type=str,
            help='comma separated HTTP methods that will be executed for all endpoints, '
                 'eg. GET,POST,DELETE [default: GET,POST,PUT,DELETE]'
        )
        methods_group.add_argument(
            '-g', '--get-only',
            action='store_true',
            default=False,
            dest='get_only',
            help='shortcut for --http-methods GET'
        )
        parser.add_argument(
            '--allow-status-codes',
            default=None,
            type=str,
            help='comma separated HTTP status codes that will be considered as success responses, '
                 'eg. 200,201,204 [default: 200,201,301,302,304,405]'
        )
        parser.add_argument(
            '--disallow-status-codes',
            default=None,
            type=str,
            help='comma separated HTTP status codes that will be considered as fail responses, '
                 'eg. 404,500'
        )
        parser.add_argument(
            '--settings',
            help=(
                'path to the Django settings module, eg. myproject.settings'
            ),
        )
        parser.add_argument(
            '--configuration',
            help=(
                'name of the configuration class to load, e.g. Development'
            ),
        )
        parser.add_argument(
            '--no-migrations',
            dest='no_migrations',
            action='store_true',
            help='flag for skipping migrations, database will be created directly from models'
        )
        parser.set_defaults(no_migrations=False)
        parser.add_argument(
            '--no-db',
            dest='no_db',
            action='store_true',
            help='flag for skipping database creation'
        )
        parser.set_defaults(no_db=False)
        parser.add_argument(
            'app_names',
            default=None,
            nargs='?',
            help='names of apps to test',
        )

    def handle(self, *args, **options):
        if options.get('get_only'):
            methods_to_test = ['GET']
        else:
            methods_to_test = self._get_list_from_string(options.get('http_methods'))
        allowed_status_codes = self._get_list_from_string(options.get('allow_status_codes'))
        disallowed_status_codes = self._get_list_from_string(options.get('disallow_status_codes'))
        disable_migrations = options.get('no_migrations')
        use_db = not options.get('no_db')
        app_names = self._get_list_from_string(options.get('app_names'))
        settings_module = options.get('settings')
        configuration = options.get('configuration')

        if allowed_status_codes and disallowed_status_codes:
            raise CommandError(
                'You can either specify --allow-status-codes or --disallow-status-codes. '
                'You must not specify both.'
            )

        generator = SmokeTestsGenerator(
            http_methods=methods_to_test,
            allowed_status_codes=allowed_status_codes,
            disallowed_status_codes=disallowed_status_codes,
            use_db=use_db,
            app_names=app_names,
            disable_migrations=disable_migrations,
            settings_module=settings_module,
            configuration=configuration,
        )
        generator.execute()

        if generator.warnings:
            self.stdout.write(
                'Some tests were skipped. Please report on '
                'https://github.com/kamilkijak/django-smoke-tests/issues.'
            )
            self.stdout.write('\n'.join(generator.warnings))

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
                int(option) if option.isdigit()
                else option.strip('/')
                for option in options.split(',')
            ]
        return None
