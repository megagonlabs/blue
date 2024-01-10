import json
import uuid
from dataclasses import dataclass

from fastapi import WebSocket


@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}
        self.session_to_client: dict = {}

    async def connect(
        self, websocket: WebSocket, connection_id: str = str(uuid.uuid4())
    ):
        await websocket.accept()
        self.active_connections[id] = websocket
        await self.send_message_to(
            websocket, json.dumps({"type": "CONNECTED", "id": id})
        )

    async def observe_session(self, connection_id: str, session_id: str):
        pass

    def disconnect(self, websocket: WebSocket):
        id = self.find_connection_id(websocket)
        del self.active_connections[id]
        return id

    def find_connection_id(self, websocket: WebSocket):
        key_list = list(self.active_connections.keys())
        val_list = list(self.active_connections.values())
        return key_list[val_list.index(websocket)]

    async def send_message_to(self, ws: WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
