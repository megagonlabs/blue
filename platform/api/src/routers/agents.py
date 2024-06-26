###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/platform/")



###### Parsers, Formats, Utils
import re
import csv
import json
import time
import logging
from utils import json_utils

###### Docker
import docker

##### Typing
from pydantic import BaseModel, Json
from typing import Union, Any, Dict, AnyStr, List

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse


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
from .settings import PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{agent_registry_id}/agents")

# set logging
logging.getLogger().setLevel("INFO")

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
                c["platform"] = la[0]
                if c["platform"] == platform_id:
                    results.append(c)
    elif PROPERTIES["platform.deploy.target"] == "swarm":
        services = client.services.list()
        results = []
        for service in services:
            c = {}
            c["id"] = service.attrs["ID"]
            c["hostname"] = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Hostname"]
            c["created_date"] = service.attrs["CreatedAt"]
            c["image"] = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Image"]
            tasks = service.tasks()
            status = None
            for task in tasks:
                s = task["Status"]["State"]
                status = s
                if status == "running":
                    break
            c["status"] = status
            labels = service.attrs["Spec"]["TaskTemplate"]["ContainerSpec"]["Labels"]
            if 'blue.agent' in labels:
                l = labels['blue.agent']
                la = l.split(".")
                c["agent"] = la[2]
                c["registry"] = la[1]
                c["platform"] = la[0]
                if c["platform"] == platform_id:
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
    # logging.info(json.dumps(containers, indent=3))

    # logging.info(json.dumps(registry_results, indent=3))
    # run through registry contents
    for registry_result in registry_results:
        t = registry_result.get('type', None)
        if t == 'agent':
            name = registry_result['name']
            # logging.info(name)

            # check if agent has a container running
            if name in containers:
                registry_result['container'] = containers[name]
            else:
                # check if parent has a container running
                # TODO: REVISIT AFTER #186
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


@router.get("/{agent_name}")
def get_agent(agent_name):
    result = agent_registry.get_agent(agent_name)
    merged_results = merge_container_results([result])
    return JSONResponse(content={"result": merged_results[0]})


@router.post("/{agent_name}")
def add_agent(agent_name, agent: Agent):
    # TODO: properties
    agent_registry.add_agent(agent_name, description=agent.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{agent_name}")
def update_agent(agent_name, agent: Agent):
    # TODO: properties
    agent_registry.update_agent(agent_name, description=agent.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{agent_name}")
def delete_agent(agent_name):
    agent_registry.remove_agent(agent_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/{agent_name}/properties")
def get_agent_properties(agent_name):
    results = agent_registry.get_agent_properties(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/{agent_name}/property/{property_name}")
def get_agent_property(agent_name, property_name):
    result = agent_registry.get_agent_property(agent_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/{agent_name}/property/{property_name}")
def set_agent_property(agent_name, property_name, property: JSONStructure):
    agent_registry.set_agent_property(agent_name, property_name, property, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{agent_name}/property/{property_name}")
def delete_agent_property(agent_name, property_name):
    agent_registry.delete_agent_property(agent_name, property_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


##### inputs
@router.get("/{agent_name}/inputs")
def get_agent_inputs(agent_name):
    results = agent_registry.get_agent_inputs(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/{agent_name}/input/{param_name}")
def get_agent_input(agent_name, param_name):
    result = agent_registry.get_agent_input(agent_name, param_name)
    return JSONResponse(content={"result": result})


@router.post("/{agent_name}/input/{param_name}")
def add_agent_input(agent_name, param_name, parameter: Parameter):
    # TODO: properties
    agent_registry.add_agent_input(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{agent_name}/input/{param_name}")
def update_agent_input(agent_name, param_name, parameter: Parameter):
    # TODO: properties
    agent_registry.update_agent_input(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{agent_name}/input/{param_name}")
def delete_agent_input(agent_name, param_name):
    agent_registry.del_agent_input(agent_name, param_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


##### outputs
@router.get("/{agent_name}/outputs")
def get_agent_outputs(agent_name):
    results = agent_registry.get_agent_outputs(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/{agent_name}/output/{param_name}")
def get_agent_output(agent_name, param_name):
    result = agent_registry.get_agent_output(agent_name, param_name)
    return JSONResponse(content={"result": result})


@router.post("/{agent_name}/output/{param_name}")
def add_agent_output(agent_name, param_name, parameter: Parameter):
    # TODO: properties
    agent_registry.add_agent_output(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.put("/{agent_name}/output/{param_name}")
def update_agent_output(agent_name, param_name, parameter: Parameter):
    # TODO: properties
    agent_registry.update_agent_output(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{agent_name}/output/{param_name}")
def delete_agent_output(agent_name, param_name):
    agent_registry.del_agent_output(agent_name, param_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/search")
def search_agents(keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    results = agent_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})
