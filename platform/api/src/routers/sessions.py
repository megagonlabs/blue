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

###### Blue
from session import Session
from blueprint import Platform
from agent_registry import AgentRegistry
from rpc import RPCClient

###### FastAPI
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Union, Any, Dict, AnyStr, List
from pydantic import BaseModel

router = APIRouter(prefix="/sessions")

###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)

###### Schema
JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


@router.get("/")
def get_sessions():
    platform = Platform(properties=PROPERTIES)
    results = platform.get_sessions()
    return JSONResponse(content={"results": results})


@router.get("/session/{session_id}")
def get_session(session_id):
    platform = Platform(properties=PROPERTIES)
    result = platform.get_session(session_id)
    return JSONResponse(content={"result": result})


@router.get("/session/{session_id}/agents")
def list_session_agents(session_id):
    platform = Platform(properties=PROPERTIES)
    session = platform.get_session(session_id)
    results = session.list_agents()
    return JSONResponse(content={"results": results})


@router.post("/session/{session_id}/agents/{registry_name}/agent/{agent_name}")
def add_agent_to_session(
    session_id,
    registry_name,
    agent_name,
    properties: JSONObject,
    input: Union[str, None] = None,
):
    platform = Platform(properties=PROPERTIES)
    session = platform.get_session(session_id)

    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    properties_from_registry = registry.get_agent_properties(agent_name)

    # start with platform properties, merge properties from registry, then merge properties from API call
    properties_from_api = properties

    p = PROPERTIES
    p = json_utils.merge_json(p, properties_from_registry)
    p = json_utils.merge_json(p, properties_from_api)

    # ASSUMPTION: agent is already deployed

    ## add agent to session
    platform.join_session(session, registry, agent_name, properties)

    return JSONResponse(content={"result": "", "message": "Success"})


# @router.delete("/{platform_name}/session/{session_id}/agents/{registry_name}/agent/{agent_name}")
# def delete_agent_to_session(session_id):
#     platform = Platform(properties=PROPERTIES)
#     session = platform.get_session(session_id)
#     #TODO
#     result = ""
#     return JSONResponse(content={"result": result, "message": "Success"})

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
    platform = Platform(properties=PROPERTIES)
    session = platform.get_session(session_id)
    if "name" in payload:
        session.set_metadata("name", payload["name"])
    if "description" in payload:
        session.set_metadata("description", payload["description"])
    return JSONResponse(content={"message": "Success"})

@router.post("/session")
async def create_session(request: Request):
    platform = Platform(properties=PROPERTIES)
    print(platform)
    result = platform.create_session()
    print(result)
    await request.app.connection_manager.broadcast(
        json.dumps({"type": "NEW_SESSION_BROADCAST", "session_id": result["id"]})
    )
    return JSONResponse(content={"result": result, "message": "Success"})


# @router.delete("/{platform_name}/session/{session_id}")
# def delete_session(session_id):
#     platform = Platform(properties=PROPERTIES)
#     platform.delete_session(session_id)
#     return JSONResponse(content={"message": "Success"})
