import random
import string
import sys
from contextlib import contextmanager
try:
    # python2
    from StringIO import StringIO
except ImportError:
    # python3
    from io import StringIO


@contextmanager
def captured_output():
    """
    Context manager that allows to catch printed output.
    """
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def create_random_string(length=5):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
