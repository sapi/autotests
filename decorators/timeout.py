import signal


class TimeoutError(Exception):
    pass


def fail_if_timeout(timeout=2):
    """
    fail_if_undefined([int]) -> function

    Fail if the decorated function does not return within the given timeout.

    Due to the constraints of signal.SIGALRM, an nonzero integer timeout must
    be provided.

    Precondition: must be applied to a TestCase class.

    """
    def handler(*args):
        raise TimeoutError()

    def decorator(fn):
        def f(self, *args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)

            signal.alarm(timeout)

            try:
                result = fn(self, *args, **kwargs)
            except TimeoutError:
                self.fail('Function execution timed out')
            finally:
                signal.signal(signal.SIGALRM, old)
                signal.alarm(0)

            return result
        return f

    return decorator
