import json
import uuid
from dataclasses import dataclass

from fastapi import WebSocket
import sys
import os

import pydash


###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agents")
sys.path.append("./lib/platform/")

###### Blue
from session import Session
from blueprint import Platform
from observer import ObserverAgent
from session import Session
from agent import Agent

###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
data_registry_id = PROPERTIES["data_registry.name"]

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)

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
            connection_id = str(hex(uuid.uuid4().fields[0]))[2:]
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        await self.send_message_to(
            websocket, json.dumps({"type": "CONNECTED", "id": connection_id})
        )

    def observe_session(self, connection_id: str, session_sid: str):
        session = Session(sid=session_sid, prefix=prefix, properties=PROPERTIES)
        agent_prefix = session.cid + ":" + "AGENT"
        pydash.objects.set_(
            self.session_to_client,
            [session_sid, connection_id],
            {
                "observer": ObserverAgent(
                    session=session,
                    prefix=agent_prefix,
                    properties={
                        **PROPERTIES,
                        "output": "websocket",
                        "websocket": "ws://localhost:5050/sessions/ws",
                        "session_id": session_sid,
                    },
                ),
                "user": Agent(
                    name="USER", id=connection_id, session=session, prefix=agent_prefix, properties=PROPERTIES
                ),
            },
        )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent = pydash.objects.get(
            self.session_to_client, [session_id, connection_id, "user"], None
        )
        if user_agent is not None:
            user_agent.interact(message)

    async def interactive_event_message(
        self, session_id: str, stream_id: str, name_id: str, timestamp: float
    ):
        pass

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
        id = self.find_connection_id(websocket)
        del self.active_connections[id]
        session_id_list = list(self.session_to_client.keys())
        for session_id in session_id_list:
            try:
                pydash.objects.unset(self.session_to_client, [session_id, id])
            except Exception as ex:
                print(ex)
        return id

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
