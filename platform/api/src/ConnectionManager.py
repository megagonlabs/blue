import json
import secrets
import time
import uuid
from dataclasses import dataclass

from fastapi import WebSocket
import sys
import os
import pydash

from server import IS_DEVELOPMENT, PLATFORM_PREFIX

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agents")
sys.path.append("./lib/platform/")

###### Blue
from constant import redisReplace
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
        if (not pydash.is_none(set_on) and time.time() - set_on < 5 * 60) or (not single_use) or (IS_DEVELOPMENT):
            connection_id = str(hex(uuid.uuid4().fields[0]))[2:]
            pydash.objects.set_(self.active_connections, connection_id, {'websocket': websocket, 'user': pydash.objects.get(self.tickets, ticket, {})})
            await self.send_message_to(
                websocket,
                json.dumps({"type": "CONNECTED", "id": redisReplace(pydash.objects.get(self.tickets, [ticket, 'email'], connection_id)), 'connection_id': connection_id}),
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
                    "user": Agent(name="USER", id=self.get_user_agent_id(connection_id), session=session, prefix=agent_prefix, properties=PROPERTIES),
                },
            )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent = pydash.objects.get(self.session_to_client, [session_id, connection_id, "user"], None)
        if user_agent is not None:
            user_agent.interact(message)

    def interactive_event_message(self, stream_id: str, name_id: str, form_id: str, timestamp: int, value):
        event_stream = Producer(cid=stream_id, properties=PROPERTIES)
        event_stream.start()
        event_stream.write(data={"name_id": name_id, "form_id": form_id, "value": value, "timestamp": timestamp}, dtype="json")

    async def observer_session_message(self, connection_id: str, session_id: str, message: str, stream: str, timestamp, mode):
        # stream is an agent identifier
        try:
            await self.send_message_to(
                self.active_connections[connection_id]['websocket'],
                json.dumps({"type": "SESSION_MESSAGE", "session_id": session_id, "message": message, "stream": stream, "timestamp": timestamp, 'mode': mode}),
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

    def get_ticket(self, user: dict = {}, single_use: bool = True):
        # default 32 nbytes ~ 43 chars
        ticket = secrets.token_urlsafe()
        # ticket is key and metadata information as value
        pydash.objects.set_(self.tickets, ticket, {**user, "set_on": time.time(), "single_use": single_use})
        return ticket

    def get_user_agent_id(self, connection_id: str):
        return redisReplace(pydash.objects.get(self.active_connections, [connection_id, "user", 'email'], connection_id))

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
