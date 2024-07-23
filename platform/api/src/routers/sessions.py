###### OS / Systems
from curses import noecho
import sys
import pydash

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/platform/")

###### Parsers, Formats, Utils
import json
import logging
from utils import json_utils
from constant import PermissionDenied, acl_enforce, d7validate
from validations.base import BaseValidation

##### Typing
from typing import Union, Any, Dict, List

###### FastAPI
from fastapi import Request
from APIRouter import APIRouter
from fastapi.responses import JSONResponse

###### Schema
JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blueprint import Platform
from agent_registry import AgentRegistry
from session import Session

###### Properties
from settings import ACL, PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/sessions")

# set logging
logging.getLogger().setLevel("INFO")

read_all_roles = ACL.get_implicit_users_for_permission('sessions', 'read_all')
read_own_roles = ACL.get_implicit_users_for_permission('sessions', 'read_own')
read_participate_roles = ACL.get_implicit_users_for_permission('sessions', 'read_participate')

write_all_roles = ACL.get_implicit_users_for_permission('sessions', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('sessions', 'write_own')
write_participate_roles = ACL.get_implicit_users_for_permission('sessions', 'write_participate')


def session_acl_enforce(request: Request, session: dict, read=False, write=False, throw=True):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    allow = False
    if (read and user_role in read_all_roles) or (write and user_role in write_all_roles):
        allow = True
    elif (read and user_role in read_own_roles) or (write and user_role in write_own_roles):
        if pydash.objects.get(session, 'created_by', None) == uid:
            allow = True
    elif (read and user_role in read_participate_roles) or (write and user_role in write_participate_roles):
        if pydash.objects.get(session, f'members.{uid}', False):
            allow = True
    if throw and not allow:
        raise PermissionDenied
    return allow


#############
@router.get("/")
def get_sessions(request: Request):
    acl_enforce(request.state.user['role'], 'sessions', ['read_all', 'read_own', 'read_participate'])
    sessions = p.get_sessions()
    results = []
    for session in sessions:
        if session_acl_enforce(request, session, read=True, throw=False):
            results.append(session)
    return JSONResponse(content={"results": results})


@router.get("/session/{session_id}")
def get_session(request: Request, session_id):
    session = p.get_session(session_id).to_dict()
    session_acl_enforce(request, session, read=True)
    return JSONResponse(content={"result": session})


@router.get("/session/{session_id}/agents")
def list_session_agents(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    return JSONResponse(content={"results": session.list_agents()})


@router.post("/session/{session_id}/agents/{registry_name}/agent/{agent_name}")
def add_agent_to_session(request: Request, session_id, registry_name, agent_name, properties: JSONObject, input: Union[str, None] = None):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    if registry_name == agent_registry_id:
        properties_from_registry = agent_registry.get_agent_properties(agent_name)

        # start with platform properties, merge properties from registry, then merge properties from API call
        properties_from_api = properties
        agent_properties = {}
        # start from platform properties
        agent_properties = json_utils.merge_json(agent_properties, PROPERTIES)
        # merge in registry properties
        agent_properties = json_utils.merge_json(agent_properties, properties_from_registry)
        # merge in properties from the api
        agent_properties = json_utils.merge_json(agent_properties, properties_from_api)

        # ASSUMPTION: agent is already deployed

        ## add agent to session
        p.join_session(session_id, registry_name, agent_name, agent_properties)

        return JSONResponse(content={"result": "", "message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.put("/session/{session_id}")
async def update_session(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    payload = await request.json()
    d7validate(
        {
            "properties": {
                "name": BaseValidation.string,
                "description": BaseValidation.string,
            }
        },
        payload,
    )

    session = p.get_session(session_id)
    if "name" in payload:
        session.set_metadata("name", payload["name"])
    if "description" in payload:
        session.set_metadata("description", payload["description"])

    return JSONResponse(content={"message": "Success"})


@router.get("/session/{session_id}/members")
def list_session_members(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    created_by = session.get_metadata("created_by")
    members: dict = session.get_metadata('members')
    results = [{'uid': created_by, 'owner': True}]
    for key in members.keys():
        if key != created_by and members[key]:
            results.append({'uid': key, 'owner': False})
    return JSONResponse(content={"results": results})


@router.post("/session/{session_id}/members/{uid}")
def add_member_to_session(request: Request, session_id, uid):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    session.set_metadata(f'members.{uid}', True)
    return JSONResponse(content={"message": "Success"})


@router.delete("/session/{session_id}/members/{uid}")
def remove_member_from_session(request: Request, session_id, uid):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    session.set_metadata(f'members.{uid}', False)
    return JSONResponse(content={"message": "Success"})


@router.post("/session")
async def create_session(request: Request):
    acl_enforce(request.state.user['role'], 'sessions', ['write_all', 'write_own'])
    session = p.create_session()
    session.set_metadata('created_by', request.state.user['uid'])
    created_date = session.get_metadata('created_date')
    result = {"id": session.sid, "name": session.sid, "description": "", 'created_date': created_date}
    await request.app.connection_manager.broadcast(json.dumps({"type": "NEW_SESSION_BROADCAST", "session": result}))
    return JSONResponse(content={"result": result})


# @router.delete("/{platform_name}/session/{session_id}")
# def delete_session(session_id):
#     p.delete_session(session_id)
#     return JSONResponse(content={"message": "Success"})
