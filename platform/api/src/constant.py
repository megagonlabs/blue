import re
from blue.platform import Platform
from blue.utils.string_utils import encode_websafe_no_padding
from fastapi import Header
import pydash
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi.responses import JSONResponse
import requests

from blue.properties import EMAIL_DOMAIN_WHITE_LIST, FIREBASE_CLIENT_ID, PROPERTIES
from settings import ACL
from datetime import timedelta

EMAIL_DOMAIN_ADDRESS_REGEXP = r"@((\w+?\.)+\w+)"
END_OF_EVENT_SIGNAL = 'END_OF_EVENT_SIGNAL'

platform_id = PROPERTIES["platform.name"]
p = Platform(id=platform_id, properties=PROPERTIES)
allowed_domains = EMAIL_DOMAIN_WHITE_LIST.split(",")

# responses
RESPONSE_501 = JSONResponse(status_code=501, content={"message": "The server lacks the ability to fulfill the request."})


def account_id_header(X_accountId: str = Header(None)):
    return


def is_email_allowed(email: str) -> bool:
    email_domain = re.search(EMAIL_DOMAIN_ADDRESS_REGEXP, email).group(1)
    urlsafe_encoded_string = encode_websafe_no_padding(email)
    result = p.get_metadata(f'settings.allowed_emails.{urlsafe_encoded_string}.allow')
    return email_domain in allowed_domains or (isinstance(result, bool) and result)


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


class PermissionDenied(Exception):
    def __init__(self):
        super().__init__()


def acl_enforce(role, resource, action, throw=True):
    result = ACL.enforce(role, resource, action)
    if not result and throw:
        raise PermissionDenied
    return result
