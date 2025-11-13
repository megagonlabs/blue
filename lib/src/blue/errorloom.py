import functools
from typing import Callable, Any, Dict, Type
from blue.blueerror import BlueError


def _create_method_wrapper(method: Callable) -> Callable:
    @functools.wraps(method)
    def method_wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as ex:
            error = ex
            if not isinstance(error, BlueError):
                error = BlueError(exception=ex)
            error.add_description("processed by loom")
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
    def __new__(mcs, name: str, bases: tuple, attrs: Dict[str, Any]):
        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            is_method = callable(attr_value) and not isinstance(attr_value, (staticmethod, classmethod))
            if is_method and attr_name != 'error_handler':
                new_attrs[attr_name] = _create_method_wrapper(attr_value)
            else:
                new_attrs[attr_name] = attr_value
        return super().__new__(mcs, name, bases, new_attrs)


class ErrorLoom(metaclass=CatcherMeta):
    def __init__(self):
        pass
