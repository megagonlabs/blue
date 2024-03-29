###### OS / Systems
from curses import noecho
import os
import sys

###### Parsers, Formats, Utils
import json
from pathlib import Path

##### Web / Sockets
from ConnectionManager import ConnectionManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

###### API Routerss
from routers import agents
from routers import data
from routers import sessions
from routers import platform

from fastapi.middleware.cors import CORSMiddleware

_VERSION_PATH = Path(__file__).parent / "version"
version = Path(_VERSION_PATH).read_text().strip()
print("blue-platform-api: " + version)

###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)
print(str(PROPERTIES))

###  Get API server address from properties to white list
api_server = PROPERTIES["api.server"]
api_server_host = ":".join(api_server.split(":")[:2])

allowed_origins = [
    "http://localhost",
    "http://localhost:3000",
    api_server_host,
    api_server_host + ":3000",
]

print(allowed_origins)

app = FastAPI()
app.include_router(agents.router)
app.include_router(data.router)
app.include_router(sessions.router)
app.include_router(platform.router)
connection_manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/sessions/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the connection from the client
    await connection_manager.connect(websocket)
    try:
        while True:
            # Receive the message from the client
            data = await websocket.receive_text()
            json_data = json.loads(data)
            connection_id = connection_manager.find_connection_id(websocket)
            if json_data["type"] == "OBSERVE_SESSION":
                connection_manager.observe_session(
                    connection_id, json_data["session_id"]
                )
            elif json_data["type"] == "USER_SESSION_MESSAGE":
                connection_manager.user_session_message(
                    connection_id, json_data["session_id"], json_data["message"]
                )
            elif json_data["type"] == "OBSERVER_SESSION_MESSAGE":
                await connection_manager.observer_session_message(
                    json_data["session_id"], json_data["message"], json_data["stream"]
                )
            print("Received", data)
    except WebSocketDisconnect:
        # Remove the connection from the list of active connections
        connection_manager.disconnect(websocket)
