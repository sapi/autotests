import config


def replace(name, value, replaceAtGlobalScope=True):
    """
    replace(str, object[, bool]) -> function

    Replace all references to the given name in each module listed in
    config.MODULES_TO_REPLACE with the given value, then restore after the
    execution of the decorated function.

    If the name also exists at global scope, then it will be replaced by
    default, but this behaviour can be overriden by setting the flag
    replaceAtGlobalScope to False.

    """
    def decorator(fn):
        def f(*args, **kwargs):
            old = []

            for module in config.MODULES_TO_REPLACE:
                try:
                    oldValue = getattr(module, name)
                except AttributeError:
                    oldValue = None

                old.append(oldValue)

                setattr(module, name, value)

            # set at local scope, but only if it already exists
            if replaceAtGlobalScope and name in globals():
                oldGlobal = globals()[name]
                globals()[name] = value

            # run the decorated function, then undo all of our changes
            try:
                result = fn(*args, **kwargs)
            finally:
                for oldValue,module in zip(old, config.MODULES_TO_REPLACE):
                    if oldValue is not None:
                        setattr(module, name, oldValue)

                if replaceAtGlobalScope and name in globals():
                    globals()[name] = oldGlobal

            return result
        return f

    return decorator
