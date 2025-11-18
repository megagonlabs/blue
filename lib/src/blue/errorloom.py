import functools
import inspect
from typing import Callable, Any, Dict
from blue.blueerror import BlueError

import contextvars

_skip_loom_context = contextvars.ContextVar('_skip_loom_context', default=False)


def skip_error_loom(func):
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
            error.add_description("processed by async loom")
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
            error.add_description("processed by sync loom")
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
    def _is_base_method_skipped(attr_name: str, bases: tuple) -> bool:
        for base in bases:
            if hasattr(base, attr_name):
                base_method = getattr(base, attr_name)
                if getattr(base_method, '__skip_error_loom__', False):
                    return True
        return False

    def __new__(mcs, name: str, bases: tuple, attrs: Dict[str, Any]):
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
    def __init__(self):
        pass
