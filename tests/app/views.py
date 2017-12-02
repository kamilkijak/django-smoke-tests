from django.http import HttpResponse

from ..decorators import decorator_with_functools_wraps, decorator_without_functools_wraps


def app_view(request, parameter):
    return HttpResponse()


@decorator_with_functools_wraps
def view_with_decorator_with_wraps(request):
    return HttpResponse()


@decorator_without_functools_wraps
def view_with_decorator_without_wraps(request):
    return HttpResponse()


def skipped_app_view(request):
    return HttpResponse()
