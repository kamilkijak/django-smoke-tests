from functools import wraps


def decorator_without_functools_wraps(f):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Exception
        return f(request, *args, **kwargs)
    return wrapper


def decorator_with_functools_wraps(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Exception
        return f(request, *args, **kwargs)
    return wrapper
