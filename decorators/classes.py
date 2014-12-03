import inspect


def apply_to_test_case_methods(decorator):
    def decorate(cls):
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            if name.startswith('test') or name in ('setUp', 'tearDown'):
                setattr(cls, name, decorator(method))

        return cls
    return decorate
