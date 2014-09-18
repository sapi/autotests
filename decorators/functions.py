class UnexpectedCallError(Exception):
    pass


def raise_if_called(*args, **kwargs):
    """
    Raise an exception if this function is called.

    This can be used as a drop-in replacement for a function which should not
    be called during normal execution.

    """
    raise UnexpectedCallError()
