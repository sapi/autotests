from functools import wraps
from StringIO import StringIO
import sys


def fail_if_print(fn):
    """
    fail_if_print(function) -> function

    Fail if any output is printed to stdout when the decorated function is run.

    Precondition: must be applied to a TestCase class.

    """
    @wraps(fn)
    def f(self, *args, **kwargs):
        sys.stdout, oldstdout = StringIO(), sys.stdout

        result = fn(self, *args, **kwargs)

        self.assertEqual(sys.stdout.getvalue(), '',
                'Unexpected output in function')

        sys.stdout = oldstdout

        return result

    return f
