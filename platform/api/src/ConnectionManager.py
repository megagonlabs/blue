import json
import uuid
from dataclasses import dataclass

from fastapi import WebSocket
import sys
import os

import pydash

sys.path.append("./lib/agents")
sys.path.append("./lib/platform/")
from observer import ObserverAgent
from session import Session
from agent import Agent
from producer import Producer

###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)


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

    def observe_session(self, connection_id: str, session_id: str):
        session = Session(name=session_id, properties=PROPERTIES)
        pydash.objects.set_(
            self.session_to_client,
            [session_id, connection_id],
            {
                "observer": ObserverAgent(
                    session=session,
                    properties={
                        **PROPERTIES,
                        "output": "websocket",
                        "websocket": "ws://localhost:5050/sessions/ws",
                        "session_id": session_id,
                    },
                ),
                "user": Agent(
                    name=f"USER:{connection_id}", session=session, properties=PROPERTIES
                ),
            },
        )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent = pydash.objects.get(
            self.session_to_client, [session_id, connection_id, "user"], None
        )
        if user_agent is not None:
            user_agent.interact(message)

    def interactive_event_message(
        self, stream_id: str, name_id: str, form_id: str, timestamp: int, value
    ):
        event_stream = Producer(name="EVENT", sid=stream_id)
        event_stream.start()
        event_stream.write(
            data={
                "name_id": name_id,
                "form_id": form_id,
                "value": value,
                "timestamp": timestamp,
            },
            dtype="json",
        )

    async def observer_session_message(
        self, session_id: str, message: str, stream: str
    ):
        # stream is an agent identifier
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
                            "stream": stream,
                        }
                    ),
                )
            except Exception as ex:
                print(ex)

    def disconnect(self, websocket: WebSocket):
        connection_id = self.find_connection_id(websocket)
        del self.active_connections[connection_id]
        session_id_list = list(self.session_to_client.keys())
        for session_id in session_id_list:
            try:
                PATH = [session_id, connection_id]
                observer_agent = pydash.objects.get(
                    self.session_to_client, PATH + ["observer"], None
                )
                user_agent = pydash.objects.get(
                    self.session_to_client, PATH + ["user"], None
                )
                if observer_agent is not None:
                    observer_agent.stop()
                if user_agent is not None:
                    user_agent.stop()
                pydash.objects.unset(self.session_to_client, PATH)
            except Exception as ex:
                print(ex)
        return connection_id

    def find_connection_id(self, websocket: WebSocket):
        key_list = list(self.active_connections.keys())
        val_list = list(self.active_connections.values())
        return key_list[val_list.index(websocket)]

    async def send_message_to(self, ws: WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await self.send_message_to(connection, message)
            except Exception as ex:
                print("broadcast", ex)
