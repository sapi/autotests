from functools import wraps


def fail_if_undefined(module, fnname):
    """
    fail_if_undefined(str) -> function

    Fail if the given name is not defined at global scope.

    Precondition: must be applied to a TestCase class.

    """
    def decorate(fn):
        @wraps(fn)
        def failed(self, *args, **kwargs):
            self.fail('%s not defined'%fnname)

        return fn if hasattr(module, fnname) else failed

    return decorate
