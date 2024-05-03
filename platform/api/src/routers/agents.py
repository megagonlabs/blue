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


###### Blue
from agent_registry import AgentRegistry

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse
from typing import Union, Any, Dict, AnyStr, List
from pydantic import BaseModel, Json

router = APIRouter(prefix="/agents")

###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)


###### Schema
class Agent(BaseModel):
    name: str
    description: Union[str, None] = None


class Parameter(BaseModel):
    name: str
    description: Union[str, None] = None


JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


@router.get("/")
def get_agents():
    registry = AgentRegistry("default", properties=PROPERTIES)
    results = registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{registry_name}")
def get_agents_from(registry_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    results = registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{registry_name}/agent/{agent_name}")
def get_agent(registry_name, agent_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_agent(agent_name)
    return JSONResponse(content={"result": result})


@router.post("/{registry_name}/agent/{agent_name}")
def add_agent(registry_name, agent_name, agent: Agent):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.add_agent(
        agent_name, description=agent.description, properties={}, rebuild=True
    )
    return JSONResponse(content={"message": "Success"})


@router.put("/{registry_name}/agent/{agent_name}")
def update_agent(registry_name, agent_name, agent: Agent):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.update_agent(
        agent_name, description=agent.description, properties={}, rebuild=True
    )
    return JSONResponse(content={"message": "Success"})


@router.delete("/{registry_name}/agent/{agent_name}")
def delete_agent(registry_name, agent_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    registry.remove_agent(agent_name, rebuild=True)
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/{registry_name}/agent/{agent_name}/properties")
def get_agent_properties(registry_name, agent_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    results = registry.get_agent_properties(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/{registry_name}/agent/{agent_name}/property/{property_name}")
def get_agent_property(registry_name, agent_name, property_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_agent_property(agent_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/{registry_name}/agent/{agent_name}/property/{property_name}")
def set_agent_property(
    registry_name, agent_name, property_name, property: JSONStructure
):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    registry.set_agent_property(
        agent_name,
        property_name,
        property,
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.delete("/{registry_name}/agent/{agent_name}/property/{property_name}")
def delete_agent_property(registry_name, agent_name, property_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    registry.delete_agent_property(
        agent_name,
        property_name,
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


##### inputs
@router.get("/{registry_name}/agent/{agent_name}/inputs")
def get_agent_inputs(registry_name, agent_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    results = registry.get_agent_inputs(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/{registry_name}/agent/{agent_name}/input/{param_name}")
def get_agent_input(registry_name, agent_name, param_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_agent_input(agent_name, param_name)
    return JSONResponse(content={"result": result})


@router.post("/{registry_name}/agent/{agent_name}/input/{param_name}")
def add_agent_input(registry_name, agent_name, param_name, parameter: Parameter):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.add_agent_input(
        agent_name,
        param_name,
        description=parameter.description,
        properties={},
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.put("/{registry_name}/agent/{agent_name}/input/{param_name}")
def update_agent_input(registry_name, agent_name, param_name, parameter: Parameter):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.update_agent_input(
        agent_name,
        param_name,
        description=parameter.description,
        properties={},
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.delete("/{registry_name}/agent/{agent_name}/input/{param_name}")
def delete_agent_input(registry_name, agent_name, param_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    registry.del_agent_input(agent_name, param_name, rebuild=True)
    return JSONResponse(content={"message": "Success"})


##### outputs
@router.get("/{registry_name}/agent/{agent_name}/outputs")
def get_agent_outputs(registry_name, agent_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    results = registry.get_agent_outputs(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/{registry_name}/agent/{agent_name}/output/{param_name}")
def get_agent_output(registry_name, agent_name, param_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_agent_output(agent_name, param_name)
    return JSONResponse(content={"result": result})


@router.post("/{registry_name}/agent/{agent_name}/output/{param_name}")
def add_agent_output(registry_name, agent_name, param_name, parameter: Parameter):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.add_agent_output(
        agent_name,
        param_name,
        description=parameter.description,
        properties={},
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.put("/{registry_name}/agent/{agent_name}/output/{param_name}")
def update_agent_output(registry_name, agent_name, param_name, parameter: Parameter):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.update_agent_output(
        agent_name,
        param_name,
        description=parameter.description,
        properties={},
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.delete("/{registry_name}/agent/{agent_name}/output/{param_name}")
def delete_agent_output(registry_name, agent_name, param_name):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    registry.del_agent_output(agent_name, param_name, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.get("/{registry_name}/search")
def search_agents(
    registry_name,
    keywords,
    approximate: bool = False,
    hybrid: bool = False,
    type: str = None,
    scope: str = None,
    page: int = 0,
    page_size: int = 10,
):
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    results = registry.search_records(
        keywords,
        type=type,
        scope=scope,
        approximate=approximate,
        hybrid=hybrid,
        page=page,
        page_size=page_size,
    )
    return JSONResponse(content={"results": results})
