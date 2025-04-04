###### OS / Systems
from curses import noecho
import sys
import pydash

###### Parsers, Formats, Utils
import json
import logging
from constant import PermissionDenied, account_id_header, acl_enforce, d7validate
from validations.base import BaseValidation

##### Typing
from typing import Union, Any, Dict, List

###### FastAPI
from fastapi import Depends, Request
from APIRouter import APIRouter
from fastapi.responses import JSONResponse

###### Schema
JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blue.agent import Agent
from blue.platform import Platform
from blue.agents.registry import AgentRegistry
from blue.utils import json_utils

###### Properties
from settings import ACL, PROPERTIES
from server import connection

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/sessions", dependencies=[Depends(account_id_header)])

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


def agent_join_session(registry_name, agent_name, properties, session_id):
    properties_from_registry = agent_registry.get_agent_properties(agent_name)

    # start with platform properties, merge properties from registry, then merge properties from API call
    properties_from_api = properties
    agent_properties = {}
    # start from platform properties
    agent_properties = json_utils.merge_json(agent_properties, PROPERTIES)
    # check if derivate agent, if so merge
    # <_name> or <_name>_<derivative__name>
    ca = agent_name.split(Agent.SEPARATOR)
    if len(ca) > 1:
        parent_agent_name = ca[0]

        parent_properties_from_registry = agent_registry.get_agent_properties(parent_agent_name)
        if parent_properties_from_registry:
            agent_properties = json_utils.merge_json(agent_properties, parent_properties_from_registry)

    # merge in registry properties
    agent_properties = json_utils.merge_json(agent_properties, properties_from_registry)
    # merge in properties from the api
    agent_properties = json_utils.merge_json(agent_properties, properties_from_api)

    # ASSUMPTION: agent is already deployed

    ## add agent to session
    p.join_session(session_id, registry_name, agent_name, agent_properties)


#############
@router.get("/")
def get_sessions(request: Request, my_sessions: bool = False):
    acl_enforce(request.state.user['role'], 'sessions', ['read_all', 'read_own', 'read_participate'])
    results = []
    uid = request.state.user['uid']
    if my_sessions:
        sessions = p.get_metadata(f'users.{uid}.sessions')
        session_ids = [*pydash.objects.keys(sessions['owner']), *pydash.objects.keys(sessions['member'])]
        for session_id in session_ids:
            if pydash.objects.get(sessions, ['owner', session_id]) or pydash.objects.get(sessions, ['member', session_id]):
                session = p.get_session(session_sid=session_id)
                if session is None:
                    continue
                session = session.to_dict()
                owner_of = pydash.is_equal(pydash.objects.get(session, 'created_by', None), uid)
                member_of = pydash.objects.get(session, f'members.{uid}', False)
                results.append({**session, 'group_by': {'owner': owner_of, 'member': not owner_of and member_of}})
    else:
        sessions = p.get_sessions()
        for session in sessions:
            if session_acl_enforce(request, session, read=True, throw=False):
                owner_of = pydash.is_equal(pydash.objects.get(session, 'created_by', None), uid)
                member_of = pydash.objects.get(session, f'members.{uid}', False)
                results.append({**session, 'group_by': {'owner': owner_of, 'member': not owner_of and member_of}})
    return JSONResponse(content={"results": results})


@router.get("/session/{session_id}")
def get_session(request: Request, session_id):
    session = p.get_session(session_id).to_dict()
    session_acl_enforce(request, session, read=True)
    uid = request.state.user['uid']
    owner_of = pydash.is_equal(pydash.objects.get(session, 'created_by', None), uid)
    member_of = pydash.objects.get(session, f'members.{uid}', False)
    return JSONResponse(content={"result": {**session, 'group_by': {'owner': owner_of, 'member': not owner_of and member_of}}})


@router.get("/session/{session_id}/agents")
def list_session_agents(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    return JSONResponse(content={"results": session.list_agents()})


@router.post("/session/{session_id}/agent/{agent_name}")
def add_agent_to_session(request: Request, session_id, agent_name, properties: JSONObject, input: Union[str, None] = None):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    agent_join_session(registry_name=agent_registry_id, session_id=session_id, agent_name=agent_name, properties=properties)
    return JSONResponse(content={"result": "", "message": "Success"})


@router.put('/session/{session_id}/pin')
def pin_session(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    uid = request.state.user['uid']
    p.set_metadata(f'users.{uid}.sessions.pinned.{session_id}', True)
    session.set_metadata(f'pinned.{uid}', True)
    return JSONResponse(content={"message": "Success"})


@router.put('/session/{session_id}/unpin')
def pin_session(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    uid = request.state.user['uid']
    p.set_metadata(f'users.{uid}.sessions.pinned.{session_id}', False)
    session.set_metadata(f'pinned.{uid}', False)
    return JSONResponse(content={"message": "Success"})


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


## members
@router.get("/session/{session_id}/members")
def list_session_members(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    created_by = session.get_metadata("created_by")
    members: dict = session.get_metadata('members')
    results = []
    if created_by is not None:
        results.append({'uid': created_by, 'owner': True})
    for key in members.keys():
        if key != created_by and members[key]:
            results.append({'uid': key, 'owner': False})
    return JSONResponse(content={"results": results})


@router.post("/session/{session_id}/members/{uid}")
def add_member_to_session(request: Request, session_id, uid):
    session = p.get_session(session_id)
    session_dict = session.to_dict()
    session_acl_enforce(request, session_dict, write=True)
    owner = pydash.objects.get(session_dict, 'owner', None)
    if pydash.is_equal(owner, uid):
        return JSONResponse(status_code=400, content={"message": "Unable to add the owner as a member."})
    session.set_metadata(f'members.{uid}', True)
    p.set_metadata(f'users.{uid}.sessions.member.{session_id}', True)
    return JSONResponse(content={"message": "Success"})


@router.delete("/session/{session_id}/members/{uid}")
def remove_member_from_session(request: Request, session_id, uid):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    session.set_metadata(f'members.{uid}', False)
    p.set_metadata(f'users.{uid}.sessions.member.{session_id}', False)
    return JSONResponse(content={"message": "Success"})


## budget
@router.get("/session/{session_id}/budget")
def get_budget(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    budget = session.get_budget()
    return JSONResponse(content={"result": budget})


@router.get("/session/{session_id}/budget/allocation")
def get_budget_allocation(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    budget_allocation = session.get_budget_allocation()
    return JSONResponse(content={"result": budget_allocation})


@router.get("/session/{session_id}/budget/use")
def get_budget_use(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    budget_use = session.get_budget_use()
    return JSONResponse(content={"result": budget_use})


@router.post("/session/{session_id}/budget/allocation/cost/{cost}")
def set_budget_allocation_cost(request: Request, session_id, cost):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    cost = float(cost)
    session.set_budget_allocation(cost=cost)
    return JSONResponse(content={"message": "Success"})


@router.post("/session/{session_id}/budget/allocation/accuracy/{accuracy}")
def set_budget_allocation_accuracy(request: Request, session_id, accuracy):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    accuracy = float(accuracy)
    session.set_budget_allocation(accuracy=accuracy)
    return JSONResponse(content={"message": "Success"})


@router.post("/session/{session_id}/budget/allocation/latency/{latency}")
def set_budget_allocation_latency(request: Request, session_id, latency):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    latency = float(latency)
    session.set_budget_allocation(latency=latency)
    return JSONResponse(content={"message": "Success"})


@router.post("/session")
async def create_session(request: Request):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    acl_enforce(user_role, 'sessions', ['write_all', 'write_own'])
    session = p.create_session(created_by=uid)
    session.set_metadata('created_by', uid)
    created_date = session.get_metadata('created_date')
    result = {"id": session.sid, "name": session.sid, "description": "", 'created_date': created_date, 'created_by': uid, 'group_by': {'owner': True, 'member': False}}
    await request.app.connection_manager.broadcast(json.dumps({"type": "NEW_SESSION_BROADCAST", "session": result}))
    return JSONResponse(content={"result": result})


@router.get("/session/{session_id}/data")
def get_session_data(request: Request, session_id):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), read=True)
    return JSONResponse(content={"result": session.get_all_data()})


@router.post('/session/{session_id}/data/{property_name}')
def set_session_data(request: Request, session_id, property_name, property: JSONStructure):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    session.set_data(property_name, pydash.objects.get(property, [property_name], None))
    return JSONResponse(content={"message": "Success"})


@router.delete('/session/{session_id}/data/{property_name}')
def delete_session_data(request: Request, session_id, property_name):
    session = p.get_session(session_id)
    session_acl_enforce(request, session.to_dict(), write=True)
    session.delete_data(property_name)
    return JSONResponse(content={"message": "Success"})


@router.post("/session/{group_name}")
async def create_session_in_group(request: Request, group_name):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    acl_enforce(user_role, 'sessions', ['write_all', 'write_own'])
    session = p.create_session(created_by=uid)
    session.set_metadata('created_by', uid)
    created_date = session.get_metadata('created_date')
    result = {"id": session.sid, "name": session.sid, "description": "", 'created_date': created_date, 'created_by': uid, 'group_by': {'owner': True, 'member': False}}
    await request.app.connection_manager.broadcast(json.dumps({"type": "NEW_SESSION_BROADCAST", "session": result}))
    # auto-join agents in group to session

    agents = agent_registry.get_agent_group_agents(group_name)
    if not pydash.is_empty(agents):
        for agent in agents:
            agent_name = agent["name"]
            agent_properties = {}
            agent_properties_from_registry = agent_registry.get_agent_properties(agent_name)
            if agent_properties_from_registry:
                agent_properties = json_utils.merge_json(agent_properties, agent_properties_from_registry)
                agent_properties_in_group = agent_registry.get_agent_group_agent_properties(group_name, agent_name)
                if agent_properties_in_group:
                    agent_properties = json_utils.merge_json(agent_properties, agent_properties_in_group)

                agent_join_session(registry_name=agent_registry_id, session_id=session.sid, agent_name=agent_name, properties=agent_properties)
    return JSONResponse(content={"result": result})


@router.delete("/session/{session_id}")
def delete_session(session_id):
    p.delete_session(session_id)
    return JSONResponse(content={"message": "Success"})
