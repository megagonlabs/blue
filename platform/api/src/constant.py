from fastapi import Header
from jsonschema.validators import Draft7Validator
import pydash
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from settings import ACL, FIREBASE_CLIENT_ID
from datetime import timedelta

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


def verify_google_id_token(id_token, client_id, issuer):
    openid_config_url = f"https://securetoken.google.com/{FIREBASE_CLIENT_ID}/.well-known/openid-configuration"
    openid_config = requests.get(openid_config_url).json()
    jwks_url = openid_config["jwks_uri"]
    jwks = requests.get(jwks_url).json()
    unverified_token = jwt.get_unverified_header(id_token)
    kid = unverified_token["kid"]
    public_key = None
    for key in jwks["keys"]:
        if key["kid"] == kid:
            public_key = RSAAlgorithm.from_jwk(key)
            break
    if not pydash.is_empty(public_key):
        decoded_token = jwt.decode(id_token, public_key, algorithms=openid_config['id_token_signing_alg_values_supported'], audience=client_id, issuer=issuer, leeway=timedelta(seconds=5))
        uid = pydash.objects.get(decoded_token, 'user_id', None)
        pydash.objects.set_(decoded_token, 'uid', uid)
        return decoded_token
    raise Exception('Empty public_key')


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


class PermissionDenied(Exception):
    def __init__(self):
        super().__init__()


def acl_enforce(role, resource, action, throw=True):
    result = ACL.enforce(role, resource, action)
    if not result and throw:
        raise PermissionDenied
    return result
