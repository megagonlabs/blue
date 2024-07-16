from jsonschema.validators import Draft7Validator
import pydash

EMAIL_DOMAIN_ADDRESS_REGEXP = r"@((\w+?\.)+\w+)"


class InvalidRequestJson(Exception):
    status_code = 422

    def __init__(self, errors, status_code=None):
        super().__init__()
        self.errors = errors
        if status_code is not None:
            self.status_code = status_code


def d7validate(validations, payload):
    errors = {}
    for error in sorted(
        Draft7Validator({"type": "object", "additionalProperties": False, **validations}).iter_errors(payload),
        key=str,
    ):
        abs_path = list(error.absolute_path)
        if len(abs_path) == 0:
            abs_path = [""]
        messages = pydash.objects.get(errors, abs_path, [])
        messages.append(error.message)
        pydash.objects.set_(errors, abs_path, messages)
    if len(errors) > 0:
        raise InvalidRequestJson(errors)


from functools import wraps
from fastapi import HTTPException
import asyncio


def isAsync(function):
    return asyncio.iscoroutinefunction(function)


def authorize(roles: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_role = pydash.objects.get(kwargs, 'request.state.user.role', None)
            if user_role not in roles:
                raise HTTPException(status_code=403, detail="You don't have permission for this request.")
            if isAsync(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
