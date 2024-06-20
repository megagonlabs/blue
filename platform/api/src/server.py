###### OS / Systems
from curses import noecho
import os
import sys


###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/data_registry/")
sys.path.append("./lib/platform/")


###### Parsers, Formats, Utils
import json
import re
import pydash
from pathlib import Path

##### FastAPI, Web, Sockets, Authentication
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth


###### API Routers
from constant import EMAIL_DOMAIN_ADDRESS_REGEXP, InvalidRequestJson
from routers import agents
from routers import data
from routers import sessions
from routers import platform
from routers import accounts

from ConnectionManager import ConnectionManager

###### Blue
from session import Session
from blueprint import Platform
from agent_registry import AgentRegistry
from data_registry import DataRegistry


###### Settings
from routers.settings import PROPERTIES, DEVELOPMENT, SECURE_COOKIE

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
data_registry_id = PROPERTIES["data_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

####### Version
_VERSION_PATH = Path(__file__).parent / "version"
version = Path(_VERSION_PATH).read_text().strip()
print("blue-platform-api: " + version)



###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)

## Create Registries, Load
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)
agent_registry.load("/blue_data/config/" + agent_registry_id + ".agents.json")

data_registry = DataRegistry(id=data_registry_id, prefix=prefix, properties=PROPERTIES)
data_registry.load("/blue_data/config/" + data_registry_id + ".data.json")

###  Get API server address from properties to white list
api_server = PROPERTIES["api.server"]
api_server_port = PROPERTIES["api.server.port"]

web_server = PROPERTIES["web.server"]
web_server_port = PROPERTIES["web.server.port"]

# only allow https or localhost connection; port must be specified
# local & cloud frontend
allowed_origins = ["http://localhost:3000", "http://localhost:25830", "https://" + web_server, "http://" + web_server + ":" + web_server_port]

app = FastAPI()
app.include_router(agents.router)
app.include_router(data.router)
app.include_router(sessions.router)
app.include_router(platform.router)
app.include_router(accounts.router)
connection_manager = ConnectionManager()
app.connection_manager = connection_manager


@app.middleware("http")
async def session_verification(request: Request, call_next):
    session_cookie = request.cookies.get("session")
    if request.method == "OPTIONS" or request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    if not session_cookie:
        if not request.url.path.startswith(f"{PLATFORM_PREFIX}/accounts/sign-in"):
            # Session cookie is unavailable. Force user to login.
            return JSONResponse(status_code=401, content={"message": "Session cookie is unavailable", "error_code": "session_cookie_unavailable"})
    # Verify the session cookie. In this case an additional check is added to detect
    # if the user's Firebase session was revoked, user deleted/disabled, etc.
    else:
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
            email = decoded_claims["email"]
            email_domain = re.search(EMAIL_DOMAIN_ADDRESS_REGEXP, email).group(1)
            request.state.user = {
                "name": decoded_claims["name"],
                "picture": decoded_claims["picture"],
                "uid": decoded_claims["uid"],
                "email_domain": email_domain,
                "email": email,
                "exp": decoded_claims["exp"],
            }
        except auth.InvalidSessionCookieError:
            # Session cookie is invalid, expired or revoked. Force user to login.
            response = JSONResponse(content={"message": "Session cookie is invalid, epxpired or revoked", "error_code": "session_cookie_invalid"}, status_code=401)
            response.set_cookie("session", expires=0, path="/")
            return response
    return await call_next(request)


@app.middleware("http")
async def health_check(request: Request, call_next):
    if request.url.path not in ["/health_check"]:
        return await call_next(request)
    return JSONResponse(content={"message": "Success"})


# middlewares are added in reverse order
# moved down so CORSMiddleware gets added before the @app.middleware("http")
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(InvalidRequestJson)
async def unicorn_exception_handler(request: Request, exc: InvalidRequestJson):
    return JSONResponse(status_code=exc.status_code, content={"json_errors": exc.errors})


@app.websocket(f"{PLATFORM_PREFIX}/sessions/ws")
async def websocket_endpoint(websocket: WebSocket, ticket: str = None):
    # Accept the connection from the client
    await connection_manager.connect(websocket, ticket)
    try:
        while True:
            # Receive the message from the client
            data = await websocket.receive_text()
            json_data = json.loads(data)
            connection_id = connection_manager.find_connection_id(websocket)
            if json_data["type"] == "OBSERVE_SESSION":
                connection_manager.observe_session(connection_id, json_data["session_id"])
            elif json_data["type"] == "REQUEST_USER_AGENT_ID":
                await connection_manager.send_message_to(websocket, json.dumps({"type": "CONNECTED", "id": connection_manager.get_user_agent_id(connection_id), 'connection_id': connection_id}))
            elif json_data["type"] == "USER_SESSION_MESSAGE":
                connection_manager.user_session_message(connection_id, json_data["session_id"], json_data["message"])
            elif json_data["type"] == "INTERACTIVE_EVENT_MESSAGE":
                connection_manager.interactive_event_message(json_data["stream_id"], json_data["name_id"], json_data["form_id"], json_data["timestamp"], pydash.objects.get(json_data, "value", None))
            elif json_data["type"] == "OBSERVER_SESSION_MESSAGE":
                await connection_manager.observer_session_message(
                    json_data["connection_id"], json_data["session_id"], json_data["message"], json_data["stream"], json_data['timestamp'], json_data['mode']
                )
    except WebSocketDisconnect:
        # Remove the connection from the list of active connections
        connection_manager.disconnect(websocket)
