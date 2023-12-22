import json
from pathlib import Path

from ConnectionManager import ConnectionManager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

_VERSION_PATH = Path(__file__).parent / "version"
version = Path(_VERSION_PATH).read_text().strip()
print("blue-platform-api: " + version)

app = FastAPI()

connection_manager = ConnectionManager()


@app.websocket("/sessions")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the connection from the client
    await connection_manager.connect(websocket)
    try:
        while True:
            # Receive the message from the client
            data = await websocket.receive_text()
            print("Received: ", data)
            # Send the message to all the clients
            await connection_manager.broadcast(data)
    except WebSocketDisconnect:
        # Remove the connection from the list of active connections
        id = connection_manager.disconnect(websocket)
        # Broadcast the disconnection of client with id to all the clients
        await connection_manager.broadcast(
            json.dumps({"type": "disconnected", "id": id})
        )


# start the server
# uvicorn server:app --port 5000 --reload
