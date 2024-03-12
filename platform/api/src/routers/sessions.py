###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append('./lib/agent_registry/')
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


###### Blue
from session import Session
from blueprint import Platform
from agent_registry import AgentRegistry
from rpc import RPCClient

###### FastAPI
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import BaseModel

router = APIRouter(prefix="/sessions")

###### Properties
PROPERTIES = os.getenv('BLUE__PROPERTIES')
PROPERTIES = json.loads(PROPERTIES)

###### Schema
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
def add_agent_to_session(platform_name, session_id, registry_name, agent_name):
    platform = Platform(properties=PROPERTIES)
    session = platform.get_session(session_id)

    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    properties = registry.get_agent_properties(agent_name)

    # assumption: agent is already deployed
    agent_rpc_host = "blue_agent_" + registry_name + "_" + agent_name

    ## create an rpc connection to launch agent
    client = RPCClient(registry_name + "_"+ agent_name, properties={"rpc.host":agent_rpc_host})
    client.connect()

    # override db.host
    properties['db.host'] = "redis"
    client.executor().launch(name=registry_name + "_" + agent_name, properties=properties)

    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

# @router.delete("/{platform_name}/session/{session_id}/agents/{registry_name}/agent/{agent_name}")
# def delete_agent_to_session(platform_name, session_id):
#     platform = Platform(platform_name)
#     session = platform.get_session(session_id)
#     #TODO
#     result = ""
#     return JSONResponse(content={"result": result, "message": "Success"})

@router.post("/session")
def create_session(platform_name):
    platform = Platform(platform_name)
    result = platform.create_session()
    return JSONResponse(content={"result": result, "message": "Success"})


# @router.delete("/{platform_name}/session/{session_id}")
# def delete_session(platform_name, session_id):
#     platform = Platform(platform_name)
#     platform.delete_session(session_id)
#     return JSONResponse(content={"message": "Success"})
