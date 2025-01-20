from fastapi import Header
from jsonschema.validators import Draft7Validator
import pydash

EMAIL_DOMAIN_ADDRESS_REGEXP = r"@((\w+?\.)+\w+)"
BANNED_ENTITY_NAMES = ['new']
END_OF_SSE_SIGNAL = 'END_OF_EVENT_SIGNAL'


def account_id_header(X_accountId: str = Header(None)):
    return


class InvalidRequestJson(Exception):
    status_code = 422

    def __init__(self, errors):
        super().__init__()
        self.errors = errors


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


from settings import ACL


class PermissionDenied(Exception):
    def __init__(self):
        super().__init__()


def acl_enforce(role, resource, action, throw=True):
    result = ACL.enforce(role, resource, action)
    if not result and throw:
        raise PermissionDenied
    return result
