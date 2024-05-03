import base64
import json
import re
import time
import datetime

import pydash
from constant import EMAIL_DOMAIN_ADDRESS_REGEXP
from fastapi import Request
import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/accounts")
import os

import firebase_admin
from firebase_admin import auth, credentials, exceptions

FIREBASE_SERVICE_CRED = os.getenv("FIREBASE_SERVICE_CRED", "{}")
cert = json.loads(base64.b64decode(FIREBASE_SERVICE_CRED))
cred = credentials.Certificate(cert)
firebase_admin.initialize_app(cred)
EMAIL_DOMAIN_WHITE_LIST = os.getenv("EMAIL_DOMAIN_WHITE_LIST", "megagon.ai")
allowed_domains = EMAIL_DOMAIN_WHITE_LIST.split(",")


@router.post("/signout")
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


@router.post("/signin")
async def signin(request: Request):
    payload = await request.json()
    id_token = pydash.objects.get(payload, "id_token", "")
    ERROR_RESPONSE = JSONResponse(
        content={"message": "Failed to create a session cookie"},
        status_code=401,
    )
    if pydash.is_empty(id_token):
        return JSONResponse(
            content={
                "message": "Illegal ID token provided: ID token must be a non-empty string."
            },
            status_code=401,
        )
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
            return JSONResponse(
                content={"message": "Invalid email domain"},
                status_code=401,
            )
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
                    },
                }
            )
            # Set cookie policy for session cookie.
            expires = datetime.datetime.now(datetime.timezone.utc) + expires_in
            response.set_cookie(
                "session",
                session_cookie,
                expires=expires,
                httponly=True,
                secure=True,
                samesite="strict",
                path="/",
            )
            return response
        return ERROR_RESPONSE
    except auth.InvalidIdTokenError:
        return JSONResponse(
            content={
                "message": "The provided ID token is not a valid Firebase ID token."
            },
            status_code=401,
        )
    except exceptions.FirebaseError:
        return ERROR_RESPONSE


@router.get("/profile")
def get_profile(request: Request):
    return JSONResponse(content={"result": request.state.user, "message": "Success"})
