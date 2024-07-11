###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/data_registry/")
sys.path.append("./lib/platform/")


###### Parsers, Formats, Utils
import re
import json
import base64
import time
import datetime
import pydash

###### FastAPI, Auth, Web
from APIRouter import APIRouter
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import auth, credentials, exceptions

from constant import EMAIL_DOMAIN_ADDRESS_REGEXP, authorize
from fastapi import Request
from APIRouter import APIRouter
from fastapi.responses import JSONResponse

###### Settings
from settings import PROPERTIES, SECURE_COOKIE, REDIS_USER_PREFIX
from server import db

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/accounts")

FIREBASE_SERVICE_CRED = os.getenv("FIREBASE_SERVICE_CRED", "{}")
cert = json.loads(base64.b64decode(FIREBASE_SERVICE_CRED))
cred = credentials.Certificate(cert)
firebase_admin.initialize_app(cred)
EMAIL_DOMAIN_WHITE_LIST = os.getenv("EMAIL_DOMAIN_WHITE_LIST", "megagon.ai")
allowed_domains = EMAIL_DOMAIN_WHITE_LIST.split(",")


def create_update_user_profile(decoded_claims):
    # create user profile with guest role if does not exist
    uid = decoded_claims['uid']
    db.json().set(
        REDIS_USER_PREFIX,
        f'$.{uid}',
        {
            "uid": uid,
            "role": "guest",
            'email': decoded_claims["email"],
            "name": decoded_claims["name"],
            "picture": decoded_claims["picture"],
        },
        nx=True,
    )
    db.json().set(REDIS_USER_PREFIX, f'$.{uid}.email', decoded_claims["email"])
    db.json().set(REDIS_USER_PREFIX, f'$.{uid}.name', decoded_claims["name"])
    db.json().set(REDIS_USER_PREFIX, f'$.{uid}.picture', decoded_claims["picture"])


@router.get('/websocket-ticket')
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def ws_ticket(request: Request):
    ticket = request.app.connection_manager.get_ticket(user=request.state.user)
    return JSONResponse(content={"ticket": ticket})


@router.post("/sign-out")
def signout(request: Request):
    session_cookie = request.cookies.get("session")
    try:
        decoded_claims = auth.verify_session_cookie(session_cookie)
        auth.revoke_refresh_tokens(decoded_claims["sub"])
        response = JSONResponse(content={"message": "Success"})
        response.set_cookie("session", expires=0, path="/")
        return response
    except auth.InvalidSessionCookieError:
        return JSONResponse(
            content={
                "message": "Session cookie is invalid, epxpired or revoked",
                "error_code": "session_cookie_invalid",
            },
            status_code=401,
        )


@router.post("/sign-in")
async def signin(request: Request):
    payload = await request.json()
    id_token = pydash.objects.get(payload, "id_token", "")
    ERROR_RESPONSE = JSONResponse(
        content={"message": "Failed to create a session cookie"},
        status_code=401,
    )
    if pydash.is_empty(id_token):
        return JSONResponse(content={"message": "Illegal ID token provided: ID token must be a non-empty string."}, status_code=401)
    try:
        decoded_claims = auth.verify_id_token(id_token)
        # {
        #     "name": "string",
        #     "picture": "url",
        #     "iss": "url",
        #     "aud": "string",
        #     "auth_time": number,
        #     "user_id": "firebase_uid",
        #     "sub": "string",
        #     "iat": number,
        #     "exp": number,
        #     "email": "email_address",
        #     "email_verified": boolean,
        #     "firebase": {
        #         "identities": {
        #             "google.com": ["google_uid"],
        #             "email": ["email_address"],
        #         },
        #         "sign_in_provider": "google.com",
        #     },
        #     "uid": "firebase_uid",
        # }
        email = decoded_claims["email"]
        email_domain = re.search(EMAIL_DOMAIN_ADDRESS_REGEXP, email).group(1)
        if email_domain not in allowed_domains:
            return JSONResponse(content={"message": "Invalid email domain"}, status_code=401)
        # Only process if the user signed in within the last 5 minutes.
        if time.time() - decoded_claims["auth_time"] < 5 * 60:
            # Set session expiration to 14 days.
            expires_in = datetime.timedelta(days=14)
            # Create the session cookie. This will also verify the ID token in the process.
            # The session cookie will have the same claims as the ID token.
            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
            response = JSONResponse(
                content={
                    "result": {
                        "name": decoded_claims["name"],
                        "picture": decoded_claims["picture"],
                        "uid": decoded_claims["uid"],
                        "email": email,
                        "email_domain": email_domain,
                        "exp": decoded_claims["exp"],
                    }
                }
            )
            # Set cookie policy for session cookie.
            expires = datetime.datetime.now(datetime.timezone.utc) + expires_in
            # samesite - lax: allow GET requests across origin
            response.set_cookie("session", session_cookie, expires=expires, httponly=True, secure=SECURE_COOKIE, samesite="lax", path="/")
            create_update_user_profile(decoded_claims)
            return response
        return ERROR_RESPONSE
    except auth.InvalidIdTokenError:
        return JSONResponse(content={"message": "The provided ID token is not a valid Firebase ID token."}, status_code=401)
    except exceptions.FirebaseError:
        return ERROR_RESPONSE


@router.post("/sign-in/cli")
async def signin_cli(request: Request):
    payload = await request.json()
    id_token = pydash.objects.get(payload, "id_token", "")
    ERROR_RESPONSE = JSONResponse(
        content={"message": "Failed to create a session cookie"},
        status_code=401,
    )
    if pydash.is_empty(id_token):
        return JSONResponse(
            content={"message": "Illegal ID token provided: ID token must be a non-empty string."},
            status_code=401,
        )
    try:
        decoded_claims = auth.verify_id_token(id_token)
        email = decoded_claims["email"]
        email_domain = re.search(EMAIL_DOMAIN_ADDRESS_REGEXP, email).group(1)
        if email_domain not in allowed_domains:
            return JSONResponse(
                content={"message": "Invalid email domain"},
                status_code=401,
            )
        if time.time() - decoded_claims["auth_time"] < 5 * 60:
            expires_in = datetime.timedelta(hours=10)
            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
            create_update_user_profile(decoded_claims)
            return JSONResponse(content={"cookie": session_cookie})
        return ERROR_RESPONSE
    except auth.InvalidIdTokenError:
        return JSONResponse(content={"message": "The provided ID token is not a valid Firebase ID token."}, status_code=401)
    except exceptions.FirebaseError:
        return ERROR_RESPONSE


@router.get("/profile")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_profile(request: Request):
    return JSONResponse(content={"profile": request.state.user})


@router.get('/profile/uid/{uid}')
def get_profile_by_uid(uid):
    user = {}
    try:
        user_record = auth.get_user(uid)
        user.update({'uid': user_record.uid, 'email': user_record.email, 'picture': user_record.photo_url, 'display_name': user_record.display_name})
    except ValueError as ex:
        print(ex)
    return JSONResponse(content={"user": user})


@router.get("/users")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_users(request: Request):
    users = db.json().get(REDIS_USER_PREFIX)
    users = list(users.values())
    if request.state.user.role != 'admin':
        for user in users:
            del user['role']
    return JSONResponse(content={"users": users})


@router.put('/users/{uid}/role/{role_name}')
@authorize(roles=['admin'])
def update_user_role(request: Request, uid, role_name):
    # preventive measure
    if uid == pydash.objects.get(request, 'state.user.uid', None):
        return JSONResponse(content={"message": "You can't modify your own role."}, status_code=400)
    user = db.json().set(REDIS_USER_PREFIX, f'$.{uid}.role', role_name)
    return JSONResponse(content={"user": user})
