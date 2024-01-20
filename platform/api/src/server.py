import json
from pathlib import Path

from ConnectionManager import ConnectionManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from routers import agents
from routers import data
from routers import sessions

from fastapi.middleware.cors import CORSMiddleware

origins = ["*", "http://localhost", "http://localhost:5050"]


_VERSION_PATH = Path(__file__).parent / "version"
version = Path(_VERSION_PATH).read_text().strip()
print("blue-platform-api: " + version)

app = FastAPI()
app.include_router(agents.router)
app.include_router(data.router)
app.include_router(sessions.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
connection_manager = ConnectionManager()


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
