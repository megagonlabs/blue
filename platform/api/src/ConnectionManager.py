import json
import uuid
from dataclasses import dataclass

from fastapi import WebSocket
import sys

import pydash

sys.path.append("./lib/agents")
sys.path.append("./lib/platform/")
from observer import ObserverAgent
from session import Session
from agent import Agent


@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}
        # { [connection_id]: websocket_connection }

        self.session_to_client: dict = {}
        # {
        #     [session_id]: {
        #         [connection_id]: { ... }
        #     }
        # }

    async def connect(self, websocket: WebSocket, connection_id: str = None):
        if pydash.is_empty(connection_id):
            connection_id = str(uuid.uuid4())
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        await self.send_message_to(
            websocket, json.dumps({"type": "CONNECTED", "id": connection_id})
        )
        print(connection_id)

    def observe_session(self, connection_id: str, session_id: str):
        session = Session(name=session_id)
        pydash.objects.set_(
            self.session_to_client,
            [session_id, connection_id],
            {
                "observer": ObserverAgent(session=session),
                "user": Agent(name=f"USER:{connection_id}", session=session),
            },
        )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent = pydash.objects.get(
            self.session_to_client, [session_id, connection_id, "user"]
        )
        user_agent.interact(message)

    async def observer_session_message(self, session_id: str, message: str):
        client_id_list = pydash.objects.get(self.session_to_client, session_id, [])
        for client_id in client_id_list:
            try:
                await self.send_message_to(
                    self.active_connections[client_id],
                    json.dumps(
                        {
                            "type": "SESSION_MESSAGE",
                            "session_id": session_id,
                            "message": message,
                        }
                    ),
                )
            except Exception as ex:
                print(ex)

    def disconnect(self, websocket: WebSocket):
        id = self.find_connection_id(websocket)
        del self.active_connections[id]
        session_id_list = list(self.session_to_client.keys())
        for session_id in session_id_list:
            pydash.objects.invoke(self.session_to_client, [session_id, "del"], id)
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
