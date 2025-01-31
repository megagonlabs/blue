###### OS / Systems
import os

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

from constant import EMAIL_DOMAIN_ADDRESS_REGEXP, account_id_header, acl_enforce
from fastapi import Depends, Request
from APIRouter import APIRouter
from fastapi.responses import JSONResponse

###### Settings
from settings import EMAIL_DOMAIN_WHITE_LIST, PROPERTIES, ROLE_PERMISSIONS, SECURE_COOKIE

### Assign from platform properties
from blue.platform import Platform

platform_id = PROPERTIES["platform.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

p = Platform(id=platform_id, properties=PROPERTIES)


##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/accounts", dependencies=[Depends(account_id_header)])

FIREBASE_SERVICE_CRED = os.getenv("FIREBASE_SERVICE_CRED", "{}")
cert = json.loads(base64.b64decode(FIREBASE_SERVICE_CRED))
cred = credentials.Certificate(cert)
firebase_admin.initialize_app(cred)
allowed_domains = EMAIL_DOMAIN_WHITE_LIST.split(",")


@router.get('/websocket-ticket')
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
            content={"message": "Session cookie is invalid, epxpired or revoked"},
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
        return JSONResponse(content={"message": "Illegal ID token provided: ID token must be a non-empty string."}, status_code=400)
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
            return JSONResponse(content={"message": "Invalid email domain"}, status_code=403)
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
            p.create_update_user(decoded_claims)
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
        return JSONResponse(content={"message": "Illegal ID token provided: ID token must be a non-empty string."}, status_code=400)
    try:
        decoded_claims = auth.verify_id_token(id_token)
        email = decoded_claims["email"]
        email_domain = re.search(EMAIL_DOMAIN_ADDRESS_REGEXP, email).group(1)
        if email_domain not in allowed_domains:
            return JSONResponse(content={"message": "Invalid email domain"}, status_code=403)
        if time.time() - decoded_claims["auth_time"] < 5 * 60:
            expires_in = datetime.timedelta(hours=10)
            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
            p.create_update_user(decoded_claims)
            return JSONResponse(content={"cookie": session_cookie})
        return ERROR_RESPONSE
    except auth.InvalidIdTokenError:
        return JSONResponse(content={"message": "The provided ID token is not a valid Firebase ID token."}, status_code=401)
    except exceptions.FirebaseError:
        return ERROR_RESPONSE


@router.put('/profile/settings/{name}')
async def set_settings(request: Request, name):
    payload = await request.json()
    p.set_metadata(f'users.{request.state.user["uid"]}.settings.{name}', payload.get('value'))
    return JSONResponse(content={"message": "Success"})


@router.get("/profile")
def get_profile(request: Request):
    user_metadata = p.get_metadata(f'users.{request.state.user["uid"]}')
    return JSONResponse(
        content={
            "profile": {
                **request.state.user,
                'permissions': pydash.objects.get(ROLE_PERMISSIONS, request.state.user['role'], {}),
                "settings": pydash.objects.get(user_metadata, 'settings', {}),
                "sessions": pydash.objects.get(user_metadata, 'sessions', {}),
            },
        }
    )


@router.get('/profile/{uid}')
def get_profile_by_uid(request: Request, uid):
    acl_enforce(request.state.user['role'], 'platform_users', 'read_all')
    user = {}
    try:
        if uid is not None:
            user_record = auth.get_user(uid)
            user.update({'uid': user_record.uid, 'email': user_record.email, 'picture': user_record.photo_url, 'name': user_record.display_name})
    except auth.UserNotFoundError as ex:
        print(ex)
    except ValueError as ex:
        print(ex)
    return JSONResponse(content={"user": user})


@router.get("/users")
def get_users(request: Request, keyword: str = ""):
    acl_enforce(request.state.user['role'], 'platform_users', 'read_all')
    users: dict = p.get_metadata('users')
    result = []
    rx = re.compile(f'(?<!\w)\s*({keyword})', re.IGNORECASE)
    for key in users.keys():
        user = users[key]
        temp = {
            'uid': user['uid'],
            'email': user['email'],
            'name': user['name'],
            'picture': user['picture'],
        }
        if re.search(rx, user['name']) is not None:
            # add user role value when querying with admin role
            if request.state.user['role'] == 'admin':
                temp['role'] = user['role']
            result.append(temp)
    return JSONResponse(content={"users": result})


@router.put('/users/{uid}/role/{role_name}')
def update_user_role(request: Request, uid, role_name):
    acl_enforce(request.state.user['role'], 'platform_users', 'write_all')
    # preventive measure
    if pydash.is_equal(uid, pydash.objects.get(request, 'state.user.uid', None)):
        return JSONResponse(content={"message": "Unable to change the role."}, status_code=400)
    p.set_metadata(f'users.{uid}.role', role_name)
    return JSONResponse(content={"message": "Success"})
