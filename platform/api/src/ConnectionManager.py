###### OS / Systems
import os
import sys


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
from blue.session import Session
from blue.platform import Platform
from blue.agent import Agent
from blue.agents.observer import ObserverAgent
from blue.pubsub import Producer
from blue.utils import uuid_utils


###### Settings
from settings import ACL, PROPERTIES, DEVELOPMENT

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)

session_read_all_roles = ACL.get_implicit_users_for_permission('sessions', 'read_all')
session_read_own_roles = ACL.get_implicit_users_for_permission('sessions', 'read_own')
session_read_participate_roles = ACL.get_implicit_users_for_permission('sessions', 'read_participate')

session_write_all_roles = ACL.get_implicit_users_for_permission('sessions', 'write_all')
session_write_own_roles = ACL.get_implicit_users_for_permission('sessions', 'write_own')
session_write_participate_roles = ACL.get_implicit_users_for_permission('sessions', 'write_participate')


def session_acl_enforce(session_sid: dict, user: dict, read=False, write=False):
    session = p.get_session(session_sid).to_dict()
    user_role = user['role']
    uid = user['uid']
    allow = False
    if (read and user_role in session_read_all_roles) or (write and user_role in session_write_all_roles):
        allow = True
    elif (read and user_role in session_read_own_roles) or (write and user_role in session_write_own_roles):
        if pydash.objects.get(session, 'created_by', None) == uid:
            allow = True
    elif (read and user_role in session_read_participate_roles) or (write and user_role in session_write_participate_roles):
        if pydash.objects.get(session, f'members.{uid}', False):
            allow = True
    return allow


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

    async def connect(self, websocket: WebSocket, ticket, debug_mode):
        await websocket.accept()
        # validate ticket
        set_on = pydash.objects.get(self.tickets, [ticket, 'set_on'], None)
        single_use = pydash.objects.get(self.tickets, [ticket, 'single_use'], True)
        if (not pydash.is_none(set_on) and time.time() - set_on < 5 * 60) or (not single_use) or (DEVELOPMENT):
            connection_id = uuid_utils.create_uuid()
            pydash.objects.set_(self.active_connections, connection_id, {'websocket': websocket, 'debug_mode': debug_mode, 'user': pydash.objects.get(self.tickets, ticket, {})})
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
        uid = self.get_user_agent_id(connection_id)
        user = {'uid': uid, 'role': pydash.objects.get(self.active_connections, [connection_id, "user", 'role'])}
        if session_acl_enforce(session_sid, user, read=True):
            # check if they are already initialized
            if not pydash.objects.has(self.session_to_client, [session_sid, connection_id]):
                user_agent = None
                if session_acl_enforce(session_sid, user, write=True):
                    user_agent: Agent = Agent(name="USER", id=uid, session=session, prefix=agent_prefix, properties=PROPERTIES)
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
                                "debug_mode": pydash.objects.get(self.active_connections, [connection_id, 'debug_mode'], False),
                            },
                        ),
                        "user": user_agent,
                    },
                )

    def user_session_message(self, connection_id: str, session_id: str, message: str):
        user_agent: Agent = pydash.objects.get(self.session_to_client, [session_id, connection_id, "user"], None)
        if user_agent is not None:
            user_agent.interact(message)

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

    def clear_session(self, session_id):
        pydash.objects.unset(self.session_to_client, session_id)

    def disconnect(self, websocket: WebSocket):
        connection_id = self.find_connection_id(websocket)
        if connection_id is None:
            return None
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
        try:
            return key_list[val_list.index(websocket)]
        except ValueError:
            return None

    async def send_message_to(self, ws: WebSocket, message: str):
        await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await self.send_message_to(connection['websocket'], message)
            except Exception as ex:
                print("ConnectionManager.broadcast", ex)
