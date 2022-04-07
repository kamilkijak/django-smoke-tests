import uuid

from django.core.management import call_command
from django.conf import settings
from django.utils.regex_helper import normalize

from django.urls import URLResolver
from unittest import skip

from .tests import SmokeTests


def get_pattern(url_pattern):
    return str(url_pattern.pattern.regex.pattern)


class HTTPMethodNotSupported(Exception):
    pass


class UrlStructureNotSupported(Exception):
    pass


class AppNotInInstalledApps(Exception):
    pass


class SmokeTestsGenerator:
    SUPPORTED_HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
    ALLOWED_STATUS_CODES = [200, 201, 301, 302, 304, 405]
    DISALLOWED_STATUS_CODES = [500, 501, 502]

    def __init__(
            self, http_methods=None, allowed_status_codes=None, disallowed_status_codes=None,
            use_db=True, app_names=None, disable_migrations=False, settings_module=None,
            configuration=None, fixture_path=None
    ):
        if http_methods:
            self.validate_custom_http_methods(http_methods)
        self.methods_to_test = http_methods or self.SUPPORTED_HTTP_METHODS
        self.allowed_status_codes = allowed_status_codes
        self.disallowed_status_codes = disallowed_status_codes or self.DISALLOWED_STATUS_CODES
        self.use_db = use_db
        self.app_names = self.validate_app_names(app_names)
        self.disable_migrations = disable_migrations
        self.settings_module = settings_module
        self.configuration = configuration
        self.fixture_path = fixture_path
        self.warnings = []

        # TODO: consider simplifying the structure below or introducing type hints
        self.all_patterns = []  # [(url_pattern, lookup_str, url_name, url_namespace, app_name),]

    def validate_custom_http_methods(self, http_methods):
        unsupported_methods = set(http_methods) - set(self.SUPPORTED_HTTP_METHODS)
        if unsupported_methods:
            raise HTTPMethodNotSupported(
                'Methods {} are not supported'.format(list(unsupported_methods))
            )

    @staticmethod
    def validate_app_names(app_names):
        for app_name in app_names or []:
            if app_name and app_name not in settings.INSTALLED_APPS:
                raise AppNotInInstalledApps(app_name)
        return app_names

    def _generate_test(self, url, method, detail_url=False):
        def test(self_of_test):
            http_method_function = getattr(self_of_test.client, method.lower(), None)
            response = http_method_function(url, {})
            additional_status_codes = [404] if detail_url else []
            if self.allowed_status_codes and (
                response.status_code not in self.allowed_status_codes + additional_status_codes
            ):
                self_of_test.fail_test(url, method, response=response)
            elif not self.allowed_status_codes and (
                response.status_code in self.disallowed_status_codes
            ):
                self_of_test.fail_test(url, method, response=response)
        return test

    @staticmethod
    def _generate_skipped_test():
        @skip('Not supported')
        def test(self_of_test):
            pass

        return test

    def execute(self):
        self.load_all_endpoints(URLResolver(r'^/', settings.ROOT_URLCONF).url_patterns)
        for url_pattern, lookup_str, url_name, url_namespace, app_name in self.all_patterns:
            if not self.app_names or self.is_url_inside_specified_app(lookup_str):
                self.create_tests_for_endpoint(url_pattern, url_name, url_namespace, app_name)

        if self.disable_migrations:
            self._disable_native_migrations()

        self._set_fixture_path()

        call_command_kwargs = self._get_call_command_kwargs()
        call_command('test', 'django_smoke_tests', **call_command_kwargs)

    @staticmethod
    def _disable_native_migrations():
        from .migrations import DisableMigrations
        settings.MIGRATION_MODULES = DisableMigrations()

    def _set_fixture_path(self):
        setattr(SmokeTests, 'fixture_path', self.fixture_path)

    def _get_call_command_kwargs(self):
        kwargs = {}

        if not self.use_db:
            kwargs['testrunner'] = 'django_smoke_tests.runners.NoDbTestRunner'

        if self.settings_module:
            kwargs['settings'] = self.settings_module

        if self.configuration:
            kwargs['configuration'] = self.configuration

        return kwargs

    def is_url_inside_specified_app(self, lookup_str):
        for app_name in self.app_names:
            if lookup_str.startswith(app_name):
                return True
        return False

    def load_all_endpoints(self, url_list, parent_url=None, parent_namespace=None, app_name=None):
        for url_pattern in url_list:
            if hasattr(url_pattern, 'url_patterns'):
                self.load_all_endpoints(
                    url_pattern.url_patterns,
                    parent_url + get_pattern(url_pattern) if parent_url else get_pattern(url_pattern),
                    ':'.join(filter(None, [parent_namespace, url_pattern.namespace])),
                    url_pattern.app_name,
                )
            else:
                self.all_patterns.append((
                    parent_url + get_pattern(url_pattern) if parent_url else get_pattern(url_pattern),
                    self.get_lookup_str(url_pattern),
                    url_pattern.name,
                    parent_namespace,
                    app_name,
                ))

    @staticmethod
    def get_lookup_str(url_pattern):
        return url_pattern.lookup_str

    def create_tests_for_endpoint(self, url_pattern, url_name, url_namespace, app_name):
        if self.is_endpoint_skipped(url_name, url_namespace, app_name):
            self.create_tests_for_http_methods(None, url_pattern, skipped=True)
        else:
            try:
                url_as_str, url_params = self.normalize_url_pattern(url_pattern)
            except UrlStructureNotSupported:
                self.warnings.append(
                    'Test skipped. URL << {} >> could not be parsed.'.format(
                        url_pattern
                    ))
                self.create_tests_for_http_methods(None, url_pattern, skipped=True)
            else:
                fake_params = {param: self.create_random_value() for param in url_params}
                url = self.create_url(url_as_str, fake_params)
                self.create_tests_for_http_methods(url, url_pattern, detail_url=bool(url_params))

    @staticmethod
    def is_endpoint_skipped(url_name, url_namespace, app_name):
        try:
            if not url_name:
                return False

            url_name_with_namespace = f'{url_namespace}:{url_name}' if url_namespace else url_name
            if url_name_with_namespace in settings.SKIP_SMOKE_TESTS:
                return True

            url_name_with_app_name = f'{app_name}:{url_name}' if app_name else url_name
            if url_name_with_app_name in settings.SKIP_SMOKE_TESTS:
                return True

            return url_name and url_name in settings.SKIP_SMOKE_TESTS
        except AttributeError:
            return False

    @staticmethod
    def normalize_url_pattern(url_pattern):
        normalized = normalize(url_pattern)

        try:
            [(url_as_str, url_params)] = normalized
        except ValueError:
            try:
                [(url_as_str_without_param, _), (url_as_str, url_params)] = normalized
            except ValueError:
                raise UrlStructureNotSupported

        if 'format' in url_params and url_as_str.endswith('.%(format)s'):
            # remove optional parameter provided by DRF ViewSet
            # eg. /items is provided as /items.%(format)s (/items.json)
            url_params.remove('format')
            url_as_str = url_as_str[:-len('.%(format)s')]

        return url_as_str, url_params

    @staticmethod
    def create_random_value():
        return uuid.uuid4()

    @staticmethod
    def create_url(url_as_str, parameters):
        url = url_as_str % parameters
        return url if url.startswith('/') else '/{}'.format(url)

    def create_tests_for_http_methods(self, url, url_pattern, detail_url=False, skipped=False):
        for method in self.methods_to_test:
            self.create_test_for_http_method(method, url, url_pattern, detail_url, skipped)

    def create_test_for_http_method(
            self, method, url, url_pattern=None, detail_url=False, skipped=False
    ):
        if skipped:
            test = self._generate_skipped_test()
        else:
            test = self._generate_test(url, method, detail_url)

        if not url_pattern:
            url_pattern = url  # url and url_pattern are the same when there are no URL parameters
        setattr(SmokeTests, self.create_test_name(method, url_pattern), test)

    @staticmethod
    def create_test_name(method, url_pattern):
        return 'test_smoke_{}_{}'.format(method, url_pattern)
