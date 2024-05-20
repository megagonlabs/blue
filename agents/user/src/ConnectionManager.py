import json
import uuid
from dataclasses import dataclass

from fastapi import WebSocket
import sys
import os
import datetime
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
from producer import Producer

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

        self.authorization_tickets: dict = {}

    async def connect(self, websocket: WebSocket, connection_id: str = None):
        if pydash.is_empty(connection_id):
            connection_id = str(hex(uuid.uuid4().fields[0]))[2:]
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        await self.send_message_to(websocket, json.dumps({"type": "CONNECTED", "id": connection_id}))

    def set_authorization_ticket(self, ticket: str, user: dict):
        # set ticket is key and metadata information as value
        # override cookie exp with WS ticket exp (5 minutes from now)
        pydash.objects.set_(
            self.authorization_tickets,
            ticket,
            {**user, "exp": datetime.datetime.now(datetime.timezone.utc).timestamp() + (5 * 60)},
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
                    properties={**PROPERTIES, "output": "websocket", "websocket": "ws://localhost:5050/sessions/ws", "session_id": session_sid},
                ),
                "user": Agent(name="USER", id=connection_id, session=session, prefix=agent_prefix, properties=PROPERTIES),
            },
        )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent = pydash.objects.get(self.session_to_client, [session_id, connection_id, "user"], None)
        if user_agent is not None:
            user_agent.interact(message)

    def interactive_event_message(self, stream_id: str, name_id: str, form_id: str, timestamp: int, value):
        event_stream = Producer(name="EVENT", sid=stream_id)
        event_stream.start()
        event_stream.write(data={"name_id": name_id, "form_id": form_id, "value": value, "timestamp": timestamp}, dtype="json")

    async def observer_session_message(self, session_id: str, message: str, stream: str, timestamp):
        # stream is an agent identifier
        client_id_list = pydash.objects.get(self.session_to_client, session_id, [])
        for client_id in client_id_list:
            try:
                await self.send_message_to(
                    self.active_connections[client_id], json.dumps({"type": "SESSION_MESSAGE", "session_id": session_id, "message": message, "stream": stream, "timestamp": timestamp})
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
                observer_agent = pydash.objects.get(self.session_to_client, PATH + ["observer"], None)
                user_agent = pydash.objects.get(self.session_to_client, PATH + ["user"], None)
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
