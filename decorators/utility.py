def tests_function(fnname):
    """
    tests_function(str) -> class

    Indicate that the given class tests a specific function.

    """
    def decorator(cls):
        cls.FUNCTION_TESTED = fnname

        return cls
    return decorator


def simple_description(desc):
    """
    simple_description(str) -> function

    Annotate the decorated function with the given description.

    """
    def decorator(fn):
        fn.SIMPLE_DESCRIPTION = desc

        return fn
    return decorator
