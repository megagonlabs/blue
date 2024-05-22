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

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse
from typing import Union, Any, Dict, AnyStr, List
from pydantic import BaseModel, Json

router = APIRouter(prefix="/agents")

###### Schema
class Agent(BaseModel):
    name: str
    description: Union[str, None] = None


class Parameter(BaseModel):
    name: str
    description: Union[str, None] = None


JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######

###### Blue
from session import Session
from blueprint import Platform
from agent_registry import AgentRegistry


###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)

#############
@router.get("/")
def get_agents():
    results = agent_registry.list_records()
    return JSONResponse(content={"results": list(results.values())})

@router.get("/{registry_name}")
def get_agents_from(registry_name):
    if registry_name == agent_registry_id:
        results = agent_registry.list_records()
        return JSONResponse(content={"results": list(results.values())})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})
    
@router.get("/{registry_name}/agent/{agent_name}")
def get_agent(registry_name, agent_name):
    if registry_name == agent_registry_id:
        result = agent_registry.get_agent(agent_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.post("/{registry_name}/agent/{agent_name}")
def add_agent(registry_name, agent_name, agent: Agent):
    if registry_name == agent_registry_id:
        # TODO: properties
        agent_registry.add_agent(agent_name, description=agent.description, properties={}, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.put("/{registry_name}/agent/{agent_name}")
def update_agent(registry_name, agent_name, agent: Agent):
    if registry_name == agent_registry_id:
        # TODO: properties
        agent_registry.update_agent(agent_name, description=agent.description, properties={}, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.delete("/{registry_name}/agent/{agent_name}")
def delete_agent(registry_name, agent_name):
    if registry_name == agent_registry_id:
        agent_registry.remove_agent(agent_name, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

##### properties
@router.get("/{registry_name}/agent/{agent_name}/properties")
def get_agent_properties(registry_name, agent_name):
    if registry_name == agent_registry_id:
        results = agent_registry.get_agent_properties(agent_name)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.get("/{registry_name}/agent/{agent_name}/property/{property_name}")
def get_agent_property(registry_name, agent_name, property_name):
    if registry_name == agent_registry_id:
        result = agent_registry.get_agent_property(agent_name, property_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.post("/{registry_name}/agent/{agent_name}/property/{property_name}")
def set_agent_property(registry_name, agent_name, property_name, property: JSONStructure):
    if registry_name == agent_registry_id:
        agent_registry.set_agent_property(agent_name, property_name, property, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.delete("/{registry_name}/agent/{agent_name}/property/{property_name}")
def delete_agent_property(registry_name, agent_name, property_name):
    if registry_name == agent_registry_id:
        agent_registry.delete_agent_property(agent_name, property_name, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

##### inputs
@router.get("/{registry_name}/agent/{agent_name}/inputs")
def get_agent_inputs(registry_name, agent_name):
    if registry_name == agent_registry_id:
        results = agent_registry.get_agent_inputs(agent_name)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.get("/{registry_name}/agent/{agent_name}/input/{param_name}")
def get_agent_input(registry_name, agent_name, param_name):
    if registry_name == agent_registry_id:
        result = agent_registry.get_agent_input(agent_name, param_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.post("/{registry_name}/agent/{agent_name}/input/{param_name}")
def add_agent_input(registry_name, agent_name, param_name, parameter: Parameter):
    if registry_name == agent_registry_id:
        # TODO: properties
        agent_registry.add_agent_input(agent_name, param_name, description=parameter.description, properties={},rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.put("/{registry_name}/agent/{agent_name}/input/{param_name}")
def update_agent_input(registry_name, agent_name, param_name, parameter: Parameter):
    if registry_name == agent_registry_id:
        # TODO: properties
        agent_registry.update_agent_input(agent_name, param_name, description=parameter.description, properties={},rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.delete("/{registry_name}/agent/{agent_name}/input/{param_name}")
def delete_agent_input(registry_name, agent_name, param_name):
    if registry_name == agent_registry_id:
        agent_registry.del_agent_input(agent_name, param_name, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

##### outputs
@router.get("/{registry_name}/agent/{agent_name}/outputs")
def get_agent_outputs(registry_name, agent_name):
    if registry_name == agent_registry_id:
        results = agent_registry.get_agent_outputs(agent_name)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.get("/{registry_name}/agent/{agent_name}/output/{param_name}")
def get_agent_output(registry_name, agent_name, param_name):
    if registry_name == agent_registry_id:
        result = agent_registry.get_agent_output(agent_name, param_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.post("/{registry_name}/agent/{agent_name}/output/{param_name}")
def add_agent_output(registry_name, agent_name, param_name, parameter: Parameter):
    if registry_name == agent_registry_id:
        # TODO: properties
        agent_registry.add_agent_output(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.put("/{registry_name}/agent/{agent_name}/output/{param_name}")
def update_agent_output(registry_name, agent_name, param_name, parameter: Parameter):
    if registry_name == agent_registry_id:
        # TODO: properties
        agent_registry.update_agent_output(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.delete("/{registry_name}/agent/{agent_name}/output/{param_name}")
def delete_agent_output(registry_name, agent_name, param_name):
    if registry_name == agent_registry_id:
        agent_registry.del_agent_output(agent_name, param_name, rebuild=True)
        # save
        agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})

@router.get("/{registry_name}/search")
def search_agents(registry_name, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    if registry_name == agent_registry_id:
        results = agent_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})