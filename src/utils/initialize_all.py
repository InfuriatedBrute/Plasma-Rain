from functools import wraps
import inspect

def _intialize_all(self, pre, names, defaults, func, *args, **kargs):
    """
    Private method better described by the methods that call it.
    """
    if pre:
        toReturn = func(self, *args, **kargs)
    for name, arg in list(zip(names[1:], args)) + list(kargs.items()):
        setattr(self, name, arg)
    if defaults:
        for name, default in zip(reversed(names), reversed(defaults)):
            if not hasattr(self, name):
                setattr(self, name, default)
    if not pre :
        toReturn = func(self, *args, **kargs)
    return toReturn


def initialize_all_pre(func):
    """
    Assigns all the variables in the input of the function to the object containing the function before running the function.
    """

    names, _, _, defaults = inspect.getargspec(func)

    @wraps(func)
    def _wrapper(self, *args, **kargs):
        _intialize_all(self, True, names, defaults, func, *args, **kargs)

    return _wrapper


def initialize_all_post(func):
    """
    Assigns all the variables in the input of the function to the object containing the function after running the function.
    """

    names, _, _, defaults = inspect.getargspec(func)

    @wraps(func)
    def _wrapper(self, *args, **kargs):
        _intialize_all(self, False, names, defaults, func, *args, **kargs)

    return _wrapper
