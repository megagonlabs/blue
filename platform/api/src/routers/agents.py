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

###### Docker
import docker

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse
from typing import Union, Any, Dict, AnyStr, List
from pydantic import BaseModel, Json
from server import PLATFORM_PREFIX

router = APIRouter(prefix=f"{PLATFORM_PREFIX}/agents")

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


###### Utility functions
def get_agent_containers():
    # connect to docker
    client = docker.from_env()

    # get list of containers based on deploy target
    if PROPERTIES["platform.deploy.target"] == "localhost":
        containers = client.containers.list()
        results = []
        for container in containers:
            c = {}
            c["id"] = container.attrs["Id"]
            c["hostname"] = container.attrs["Config"]["Hostname"]
            c["created_date"] = container.attrs["Created"]
            c["image"] = container.attrs["Config"]["Image"]
            c["status"] = container.attrs["State"]["Status"]
            labels = container.attrs["Config"]["Labels"]
            if 'blue.agent' in labels:
                l = labels['blue.agent']
                la = l.split(".")
                c["agent"] = la[2]
                c["registry"] = la[1]
            results.append(c)
    elif PROPERTIES["platform.deploy.target"] == "swarm":
        services = client.services.list()
        results = []
        for service in services:
            c = {}
            c["id"] = service.attrs["ID"]
            c["hostname"] = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"][
                "Hostname"
            ]
            c["created_date"] = service.attrs["CreatedAt"]
            c["image"] = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Image"]
            labels = container.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Labels"]
            if 'blue.agent' in labels:
                l = labels['blue.agent']
                la = l.split(".")
                c["agent"] = la[2]
                c["registry"] = la[1]
            results.append(c)

    # build dictionary of container results <registry_name>.<agent_name>
    containers = {}
    for result in results:
        if 'agent' in result:
            agent = result['agent']
            registry = None
            if 'registry' in result:
                registry = result['registry']
            
            if registry == None:
                continue 
            if registry == agent_registry_id:
                containers[agent] = result

    # close connection
    client.close()
    
    return containers

def merge_container_results(registry_results):
    containers = get_agent_containers()
    #logging.info(json.dumps(containers, indent=3))

    # run through registry contents
    for registry_result in registry_results:
        t = registry_result['type']
        if t == 'agent':
            name = registry_result['name']

            # TODO: REVISIT AFTE #186
            name = name.split("_")[0]
            
            if name in containers:
                registry_result['container'] = containers[name]
            else:
                registry_result['container'] = {"status": "not exist"}
        
    return registry_results

#############
@router.get("/")
def get_agents():
    registry_results = agent_registry.list_records()
    registry_results = list(registry_results.values())
    merged_results = merge_container_results(registry_results)
    return JSONResponse(content={"results": merged_results})

@router.get("/{registry_name}")
def get_agents_from(registry_name):
    if registry_name == agent_registry_id:
        registry_results = agent_registry.list_records()
        registry_results = list(registry_results.values())
        merged_results = merge_container_results(registry_results)
        return JSONResponse(content={"results": merged_results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})
    
@router.get("/{registry_name}/agent/{agent_name}")
def get_agent(registry_name, agent_name):
    if registry_name == agent_registry_id:
        result = agent_registry.get_agent(agent_name)
        merged_results = merge_container_results([result])
        return JSONResponse(content={"result": merged_results[0]})
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
    

