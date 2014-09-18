def fail_if_undefined(module, fnname):
    """
    fail_if_undefined(str) -> function

    Fail if the given name is not defined at global scope.

    Precondition: must be applied to a TestCase class.

    """
    try:
        getattr(module, fnname)
    except AttributeError:
        return lambda f: \
                (lambda self, *args, **kwargs: self.fail(
                    '%s not defined'%fnname))

    return lambda f: f
