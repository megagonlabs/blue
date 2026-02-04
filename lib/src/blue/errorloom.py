import functools
import inspect
from typing import Callable, Any, Dict
from blue.blueerror import BlueError

import contextvars

# Context variable to control skipping error handling logic dynamically within call stacks.
_skip_loom_context = contextvars.ContextVar('_skip_loom_context', default=False)


def skip_error_loom(func):
    """
    Decorator to exempt a specific method or function from `ErrorLoom` processing.

    When a method is decorated with `@skip_error_loom`, the `CatcherMeta` metaclass will
    bypass wrapping it with the error handling logic. It also sets a context variable
    so that any internal calls made by this function are also skipped.

    This supports both synchronous and asynchronous functions.

    Parameters:
        func (Callable): The function or method to skip.

    Returns:
        Callable: The original function wrapped in a context manager that sets the skip flag.
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        token = _skip_loom_context.set(True)
        try:
            return await func(*args, **kwargs)
        finally:
            _skip_loom_context.reset(token)

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        token = _skip_loom_context.set(True)
        try:
            return func(*args, **kwargs)
        finally:
            _skip_loom_context.reset(token)

    if inspect.iscoroutinefunction(func):
        setattr(async_wrapper, '__skip_error_loom__', True)
        return async_wrapper
    else:
        setattr(sync_wrapper, '__skip_error_loom__', True)
        return sync_wrapper


def _create_async_method_wrapper(method: Callable) -> Callable:
    """
    Internal helper to wrap an asynchronous method with error handling logic.

    If an exception occurs during execution:

    1. It wraps the exception in a `BlueError` (if it isn't one already).
    2. It checks if the instance has an `error_handler` method.
    3. If `error_handler` exists, it delegates the error there.
    4. If not, it logs the error to stdout and re-raises it.

    Parameters:
        method (Callable): The async method to wrap.

    Returns:
        Callable: The wrapped async method.
    """

    @functools.wraps(method)
    async def method_wrapper(self, *args, **kwargs):
        if _skip_loom_context.get():
            return await method(self, *args, **kwargs)
        try:
            return await method(self, *args, **kwargs)
        except Exception as ex:
            error = ex
            if not isinstance(error, BlueError):
                error = BlueError(exception=ex)
            if hasattr(self, 'error_handler') and callable(self.error_handler):
                error_handler = getattr(self, 'error_handler')
                error_handler(error=error, exception=ex)
            else:
                # log error here
                print(error)
                raise error
            return None

    return method_wrapper


def _create_sync_method_wrapper(method: Callable) -> Callable:
    """
    Internal helper to wrap a synchronous method with error handling logic.

    Behaves identically to `_create_async_method_wrapper` but for blocking functions.

    Parameters:
        method (Callable): The sync method to wrap.

    Returns:
        Callable: The wrapped sync method.
    """

    @functools.wraps(method)
    def method_wrapper(self, *args, **kwargs):
        if _skip_loom_context.get():
            return method(self, *args, **kwargs)
        try:
            return method(self, *args, **kwargs)
        except Exception as ex:
            error = ex
            is_blue_error = isinstance(error, BlueError)
            if not is_blue_error:
                error = BlueError(exception=ex)
            if hasattr(self, 'error_handler') and callable(self.error_handler):
                error_handler = getattr(self, 'error_handler')
                error_handler(error=error, exception=ex)
            else:
                # log error here
                print(error)
                raise error
            return None

    return method_wrapper


class CatcherMeta(type):
    """
    Metaclass that automatically wraps all methods of a class with error handling logic.

    When a class uses `CatcherMeta` (or inherits from `ErrorLoom`), this metaclass:

    1. Iterates through all attributes defined in the class body.
    2. Identifies callable methods (excluding static/class methods).
    3. Wraps them with `_create_async_method_wrapper` or `_create_sync_method_wrapper`.
    4. Respects the `@skip_error_loom` decorator to bypass wrapping.
    5. Checks base classes to see if a method was explicitly skipped in a higher class, preserving that exemption in the lower class.
    """

    def _is_base_method_skipped(attr_name: str, bases: tuple) -> bool:
        """
        Checks if a method with the given name was marked to be skipped in any of the base classes.

        Parameters:
            attr_name (str): The name of the method to check.
            bases (tuple): The base classes of the class being created.

        Returns:
            bool: True if the method is skipped in any base class, False otherwise.
        """
        for base in bases:
            if hasattr(base, attr_name):
                base_method = getattr(base, attr_name)
                if getattr(base_method, '__skip_error_loom__', False):
                    return True
        return False

    def __new__(mcs, name: str, bases: tuple, attrs: Dict[str, Any]):
        """
        Constructs the new class, intercepting and wrapping its methods.
        """
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            is_method = callable(attr_value) and not isinstance(attr_value, (staticmethod, classmethod))
            is_explicitly_skipped = getattr(attr_value, '__skip_error_loom__', False)
            is_inherited_skipped = mcs._is_base_method_skipped(attr_name, bases)
            if is_method and attr_name != 'error_handler':
                if is_explicitly_skipped:
                    new_attrs[attr_name] = attr_value
                elif is_inherited_skipped:
                    new_attrs[attr_name] = skip_error_loom(attr_value)
                else:
                    if inspect.iscoroutinefunction(attr_value):
                        new_attrs[attr_name] = _create_async_method_wrapper(attr_value)
                    else:
                        new_attrs[attr_name] = _create_sync_method_wrapper(attr_value)
            else:
                new_attrs[attr_name] = attr_value
        return super().__new__(mcs, name, bases, new_attrs)


class ErrorLoom(metaclass=CatcherMeta):
    """
    Base class for automatic error handling.

    Classes inheriting from `ErrorLoom` will have all their methods automatically
    wrapped in a try/except block. Caught exceptions are converted to `BlueError`
    objects and passed to an `error_handler` method if one is defined on the instance.

    To exempt a method from this behavior, use the `@skip_error_loom` decorator.
    """

    def __init__(self):
        pass
