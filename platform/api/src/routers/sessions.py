###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/platform/")


######
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils
from constant import d7validate
from validations.base import BaseValidation

##### Typing
from pydantic import BaseModel, Json
from typing import Union, Any, Dict, AnyStr, List

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
from session import Session
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
def get_sessions():
    results = p.get_sessions()
    return JSONResponse(content={"results": results})


@router.get("/session/{session_id}")
def get_session(session_id):
    result = p.get_session(session_id)
    return JSONResponse(content={"result": result})


@router.get("/session/{session_id}/agents")
def list_session_agents(session_id):
    session = p.get_session(session_id)
    results = session.list_agents()
    return JSONResponse(content={"results": results})


@router.post("/session/{session_id}/agents/{registry_name}/agent/{agent_name}")
def add_agent_to_session(session_id, registry_name, agent_name, properties: JSONObject, input: Union[str, None] = None):
    if registry_name == agent_registry_id:
        session = p.get_session(session_id)
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


@router.post("/session")
async def create_session(request: Request):
    result = p.create_session()

    await request.app.connection_manager.broadcast(json.dumps({"type": "NEW_SESSION_BROADCAST", "session": result}))
    return JSONResponse(content={"result": result, "message": "Success"})


# @router.delete("/{platform_name}/session/{session_id}")
# def delete_session(session_id):
#     p.delete_session(session_id)
#     return JSONResponse(content={"message": "Success"})
