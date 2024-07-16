###### OS / Systems
from curses import noecho
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/platform/")

###### Parsers, Formats, Utils
import json
from utils import json_utils
from constant import authorize, d7validate
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

###### Properties
from settings import PROPERTIES

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


#############
@router.get("/")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_sessions(request: Request):
    results = p.get_sessions()
    return JSONResponse(content={"results": results})


@router.get("/session/{session_id}")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_session(request: Request, session_id):
    result = p.get_session(session_id)
    return JSONResponse(content={"result": result})


@router.get("/session/{session_id}/agents")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def list_session_agents(request: Request, session_id):
    session = p.get_session(session_id)
    results = session.list_agents()
    return JSONResponse(content={"results": results})


@router.post("/session/{session_id}/agents/{registry_name}/agent/{agent_name}")
@authorize(roles=['admin', 'member', 'developer'])
def add_agent_to_session(request: Request, session_id, registry_name, agent_name, properties: JSONObject, input: Union[str, None] = None):
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
@authorize(roles=['admin', 'member', 'developer'])
async def update_session(request: Request, session_id):
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
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def list_session_members(request: Request, session_id):
    session = p.get_session(session_id)
    created_by = session.get_metadata("created_by")
    members: dict = session.get_metadata('members')
    results = [{'uid': created_by, 'owner': True}]
    for key in members.keys():
        if key != created_by and members[key]:
            results.append({'uid': key, 'owner': False})
    return JSONResponse(content={"results": results})


@router.post("/session/{session_id}/members/{uid}")
@authorize(roles=['admin', 'member', 'developer'])
def add_member_to_session(request: Request, session_id, uid):
    session = p.get_session(session_id)
    session.set_metadata(f'members.{uid}', True)
    return JSONResponse(content={"message": "Success"})


@router.delete("/session/{session_id}/members/{uid}")
@authorize(roles=['admin', 'member', 'developer'])
def remove_member_from_session(request: Request, session_id, uid):
    session = p.get_session(session_id)
    session.set_metadata(f'members.{uid}', False)
    return JSONResponse(content={"message": "Success"})


@router.post("/session")
@authorize(roles=['admin', 'member', 'developer'])
async def create_session(request: Request):
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
