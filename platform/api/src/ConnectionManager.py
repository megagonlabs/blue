###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agents")
sys.path.append("./lib/platform/")


###### Parsers, Formats, Utils
import json
import time
import uuid
import pydash
import secrets

##### FastAPI, Web, Sockets, Authentication
from fastapi import WebSocket
from dataclasses import dataclass

###### Blue
from session import Session
from blueprint import Platform
from observer import ObserverAgent
from session import Session
from agent import Agent
from producer import Producer

from message import Message, MessageType, ContentType, ControlCode


###### Settings
from settings import PROPERTIES, DEVELOPMENT

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
data_registry_id = PROPERTIES["data_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)


@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict = {}
        # {
        #     [connection_id]: {
        #         websocket,
        #         user
        #     }
        # }

        self.session_to_client: dict = {}
        # {
        #     [session_id]: {
        #         [connection_id]: { ... }
        #     }
        # }

        self.tickets: dict = {}

    async def connect(self, websocket: WebSocket, ticket):
        await websocket.accept()
        # validate ticket
        set_on = pydash.objects.get(self.tickets, [ticket, 'set_on'], None)
        single_use = pydash.objects.get(self.tickets, [ticket, 'single_use'], True)
        if (not pydash.is_none(set_on) and time.time() - set_on < 5 * 60) or (not single_use) or (DEVELOPMENT):
            connection_id = str(hex(uuid.uuid4().fields[0]))[2:]
            pydash.objects.set_(self.active_connections, connection_id, {'websocket': websocket, 'user': pydash.objects.get(self.tickets, ticket, {})})
            await self.send_message_to(
                websocket,
                json.dumps({"type": "CONNECTED", "id": pydash.objects.get(self.tickets, [ticket, 'uid'], connection_id), 'connection_id': connection_id}),
            )
        else:
            await websocket.close()
        # delete ticket if single_use = True
        if single_use:
            pydash.objects.unset(self.tickets, ticket)

    def observe_session(self, connection_id: str, session_sid: str):
        session = Session(sid=session_sid, prefix=prefix, properties=PROPERTIES)
        agent_prefix = session.cid + ":" + "AGENT"
        ticket = self.get_ticket(single_use=False)
        # check session access permission
        created_by = session.get_metadata("created_by")
        members: dict = session.get_metadata('members')
        uid = self.get_user_agent_id(connection_id)
        if uid == created_by or uid in members:
            # check if they are already initialized
            if not pydash.objects.has(self.session_to_client, [session_sid, connection_id]):
                pydash.objects.set_(
                    self.session_to_client,
                    [session_sid, connection_id],
                    {
                        "observer": ObserverAgent(
                            session=session,
                            prefix=agent_prefix,
                            properties={
                                **PROPERTIES,
                                "output": {
                                    'type': "websocket",
                                    "mode": "streaming",
                                    "websocket": f"ws://localhost:5050{PLATFORM_PREFIX}/sessions/ws?ticket={ticket}",
                                },
                                "session_id": session_sid,
                                "connection_id": connection_id,
                            },
                        ),
                        "user": Agent(name="USER", id=uid, session=session, prefix=agent_prefix, properties=PROPERTIES),
                    },
                )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent = pydash.objects.get(self.session_to_client, [session_id, connection_id, "user"], None)
        if user_agent is not None:
            user_agent.interact(message, output="TEXT")

    def interactive_event_message(self, json_data):
        if json_data["stream_id"] is not None:
            event_stream = Producer(cid=json_data["stream_id"], properties=PROPERTIES)
            event_stream.start()
            event_stream.write_data(
                {
                    "path": pydash.objects.get(json_data, "path", None),
                    "action": pydash.objects.get(json_data, "action", None),
                    "form_id": json_data['form_id'],
                    "value": pydash.objects.get(json_data, "value", None),
                    "timestamp": json_data['timestamp'],
                }
            )

    async def observer_session_message(self, connection_id: str, message):
        # stream is an agent identifier
        try:
            await self.send_message_to(
                self.active_connections[connection_id]['websocket'],
                json.dumps({**message, "type": "SESSION_MESSAGE"}),
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
                pydash.objects.unset(self.active_connections, connection_id)
            except Exception as ex:
                print(ex)
        return connection_id

    def get_ticket(self, user: dict = {}, single_use: bool = True):
        # default 32 nbytes ~ 43 chars
        ticket = secrets.token_urlsafe() + str(int(time.time()))
        # ticket is key and metadata information as value
        pydash.objects.set_(self.tickets, ticket, {**user, "set_on": time.time(), "single_use": single_use})
        return ticket

    def get_user_agent_id(self, connection_id: str):
        return pydash.objects.get(self.active_connections, [connection_id, "user", 'uid'], connection_id)

    def find_connection_id(self, websocket: WebSocket):
        key_list = list(self.active_connections.keys())
        val_list = [value['websocket'] for value in self.active_connections.values()]
        return key_list[val_list.index(websocket)]

    async def send_message_to(self, ws: WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await self.send_message_to(connection['websocket'], message)
            except Exception as ex:
                print("ConnectionManager.broadcast", ex)
