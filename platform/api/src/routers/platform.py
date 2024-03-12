###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append('./lib/agent_registry/')
sys.path.append('./lib/data_registry/')
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

###### Blue
from session import Session
from blueprint import Platform
from agent_registry import AgentRegistry
from rpc import RPCClient

###### FastAPI
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Union, Any, Dict, AnyStr, List
from pydantic import BaseModel, Json

router = APIRouter(prefix="/platform")

###### Properties
PROPERTIES = os.getenv('BLUE__PROPERTIES')
PROPERTIES = json.loads(PROPERTIES)

###### Schema
JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######

@router.get("/registry/agents/") 
#get the list of agent registries on platform
def list_agent_registries():
    platform = Platform(properties=PROPERTIES)
    results = []
    return JSONResponse(content={"results": results})

@router.get("/registry/agents/{registry_name}") 
#get agent registry info on platform for registry with name {registry_name}
def get_agent_registry(registry_name):
    platform = Platform(properties=PROPERTIES)
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.post("registry/agents/{registry_name}") 
#create a new agent registry on platform, deploy registry container and start registry
def create_agent_registry(registry_name, properties: JSONObject):
    platform = Platform(properties=PROPERTIES)
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.delete("/registry/agents/{registry_name}") 
#delete agent registry on platform, stop registry container
def delete_agent_registry():
    platform = Platform(properties=PROPERTIES)
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.get("/registry/data/") 
#get the list of data registries on platform
def list_data_registries():
    platform = Platform(properties=PROPERTIES)
    results = []
    return JSONResponse(content={"results": results})

@router.get("/registry/data/{registry_name}") 
#get data registry info on platform for registry with name {registry_name}
def get_data_registry(registry_name):
    platform = Platform(properties=PROPERTIES)
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.post("registry/data/{registry_name}?properties={}") 
#create a new data registry on platform, deploy registry container and start registry
def create_data_registry(registry_name, properties: JSONObject):
    platform = Platform(properties=PROPERTIES)
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.delete("/registry/data/{registry_name}") 
#delete data registry on platform, stop registry container
def delete_data_registry():
    platform = Platform(properties=PROPERTIES)
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.get("/agents/") 
#get the list of agent running agents on the platform
def list_agent_containers():
    platform = Platform(properties=PROPERTIES)

    # connect to docker
    client = docker.from_env()

    # get list of containers based on deploy target
    if PROPERTIES['platform.deploy.target'] == 'localhost':
        containers = client.containers.list()
        results = []
        for container in containers:
            c = {}
            c['id'] = container.attrs['Id']
            c['hostname'] = container.attrs['Config']['Hostname']
            c['created_date'] = container.attrs['Created']
            c['image'] = container.attrs['Config']['Image']
            c['status'] = container.attrs['State']['Status']
            if c['hostname'].find('blue_agent') < 0:
                continue
            hs = c['hostname'].split("_")
            c['agent'] = hs[3]
            c['registry'] = hs[2]
            results.append(c)
    elif PROPERTIES['platform.deploy.target'] == 'swarm':
        services = client.services.list()
        results = []
        for service in services:
            c = {}
            c['id'] = service.attrs['ID']
            c['hostname'] = service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Hostname']
            c['created_date'] = service.attrs['CreatedAt']
            c['image'] = service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
            if c['hostname'].find('blue_agent') < 0:
                continue
            hs = c['hostname'].split("_")
            c['agent'] = hs[3]
            c['registry'] = hs[2]
            results.append(c)

    return JSONResponse(content={"results": results})

@router.post("/agents/{registry_name}/agent/{agent_name}") 
#deploy an agent container with the name {agent_name} to the agent registry with the name {registry_name}
def deploy_agent_container(registry_name, agent_name):
    platform = Platform(properties=PROPERTIES)

    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    agent = registry.get_agent_properties(agent_name)
    properties = registry.get_agent_properties(agent_name)
    image = properties['image']

    # connect to docker
    client = docker.from_env()

    # deploy agent container based on deploy target
    if PROPERTIES['platform.deploy.target'] == 'localhost':
        client.containers.run(image, '--serve',
            network="blue_platform_" + PROPERTIES['platform.name'] + "_network_bridge",
            hostname="blue_agent_" + registry_name + "_" + agent_name, stdout=True, stderr=True)
    elif PROPERTIES['platform.deploy.target'] == 'swarm':
        constraints = ["node.labels.target==agent"]
        client.services.create(image, args=['--serve'],
            networks=["blue_platform_" + PROPERTIES['platform.name'] + "_network_overlay"], constraints=constraints,
            hostname="blue_agent_" + registry_name + "_" + agent_name) 
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.put("/agents/{registry_name}/agent/{agent_name}") 
#update the agent container with the name {agent_name} in the agent registry with the name {registry_name}, pulling in new image
def update_agent_container(registry_name, agent_name):
    platform = Platform(properties=PROPERTIES)
    
    registry = AgentRegistry(registry_name, properties=PROPERTIES)
    agent = registry.get_agent_properties(agent_name)
    properties = registry.get_agent_properties(agent_name)
    image = properties['image']

    # connect to docker
    client = docker.from_env()

    if PROPERTIES['platform.deploy.target'] == 'localhost':
        client.images.pull(image)
    elif PROPERTIES['platform.deploy.target'] == 'swarm':
        # TODO: pull image on all nodes where label.target==agent
        pass
    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})

@router.delete("agents/{registry_name}/agent/{agent_name}") 
#shutdown the agent container with the name {agent_name} from the agent registry with the name {registry_name}
def shutdown_agent_container(registry_name, agent_name):
    platform = Platform(properties=PROPERTIES)
    
    # connect to docker
    client = docker.from_env()

    if PROPERTIES['platform.deploy.target'] == 'localhost':
        containers = client.containers.list()
        results = []
        for container in containers:
            h = container.attrs['Config']['Hostname']
            if h.find('blue_agent') < 0:
                continue
            hs = h.split("_")
            a = hs[3]
            r = hs[2]
            if r == registry_name and a == agent_name:
                container.stop()
    elif PROPERTIES['platform.deploy.target'] == 'swarm':
        services = client.services.list()
        for service in services:
            print(service) 
            # service.remove()

    result = ""
    return JSONResponse(content={"result": result, "message": "Success"})
