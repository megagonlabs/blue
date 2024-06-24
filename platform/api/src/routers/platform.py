###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/data_registry/")
sys.path.append("./lib/platform/")


###### Parsers, Formats, Utils
import re
import time
import csv
import uuid
import random
import json
import logging
from utils import json_utils

###### Docker
import docker

##### Typing
from pydantic import BaseModel, Json
from typing import Union, Any, Dict, AnyStr, List

###### FastAPI, Web, Auth
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
from .settings import PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
data_registry_id = PROPERTIES["data_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'


###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)


##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/containers")

# set logging
logging.getLogger().setLevel("INFO")

@router.get("/agents/")
# get the list of agent running agents on the platform
def list_agent_containers():
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

    # close connection
    client.close()

    return JSONResponse(content={"results": results})


@router.post("/agents/agent/{agent_name}")
# deploy an agent container with the name {agent_name} to the agent registry with the name
def deploy_agent_container(agent_name):
   
    agent_registry_properties = agent_registry.get_agent_properties(agent_name)
    image = agent_registry_properties["image"]

    # connect to docker
    client = docker.from_env()

    # agent factory properties
    agent_properties = {}

    # start from platform properties
    agent_properties = json_utils.merge_json(agent_properties, PROPERTIES)

    # override with registry properties
    agent_properties = json_utils.merge_json(agent_properties, agent_registry_properties)

    # deploy agent container based on deploy target
    if PROPERTIES["platform.deploy.target"] == "localhost":
        client.containers.run(
            image,
            "--serve " + agent_name + " " + "--platform " + platform_id +  " " + + "--registry " + agent_registry_id + " " + "--properties " + "'" + json.dumps(agent_properties) + "'",
            network="blue_platform_" + PROPERTIES["platform.name"] + "_network_bridge",
            hostname="blue_agent_" + agent_registry_id + "_" + agent_name,
            volumes=["blue_" + platform_id + "_data:/blue_data"],
            labels={"blue.agent": PROPERTIES["platform.name"] + "." + agent_registry_id + "." + agent_name},
            stdout=True,
            stderr=True,
        )
    elif PROPERTIES["platform.deploy.target"] == "swarm":
        constraints = ["node.labels.target==agent"]
        client.services.create(
            image,
            args=["--serve", agent_name, "--platform", platform_id, "--registry", agent_registry_id, "--properties", json.dumps(agent_properties)],
            networks=["blue_platform_" + PROPERTIES["platform.name"] + "_network_overlay"],
            constraints=constraints,
            hostname="blue_agent_" + agent_registry_id + "_" + agent_name,
            mounts=["blue_" + platform_id + "_data:/blue_data"],
            container_labels={"blue.agent": PROPERTIES["platform.name"] + "." + agent_registry_id + "." + agent_name},
        )
    result = ""

    # close connection
    client.close()

    return JSONResponse(content={"result": result, "message": "Success"})


@router.put("/agents/agent/{agent_name}")
# update the agent container with the name {agent_name} in the agent registry with the name, pulling in new image
def update_agent_container(registry_name, agent_name):
    agent = agent_registry.get_agent_properties(agent_name)
    properties = agent_registry.get_agent_properties(agent_name)
    image = properties["image"]

    # connect to docker
    client = docker.from_env()

    if PROPERTIES["platform.deploy.target"] == "localhost":
        client.images.pull(image)
    elif PROPERTIES["platform.deploy.target"] == "swarm":
        # TODO: pull image on all nodes where label.target==agent
        pass
    result = ""

    # close connection
    client.close()

    return JSONResponse(content={"result": result, "message": "Success"})


@router.delete("/agents/agent/{agent_name}")
# shutdown the agent container with the name {agent_name} from the agent registry with the name
def shutdown_agent_container(registry_name, agent_name):
    platform = Platform(id=platform_id, properties=PROPERTIES)

    # connect to docker
    client = docker.from_env()

    if PROPERTIES["platform.deploy.target"] == "localhost":
        containers = client.containers.list()
        results = []
        for container in containers:
            h = container.attrs["Config"]["Hostname"]
            if h.find("blue_agent") < 0:
                continue
            hs = h.split("_")
            a = hs[3]
            r = hs[2]
            if r == registry_name and a == agent_name:
                container.stop()
    elif PROPERTIES["platform.deploy.target"] == "swarm":
        services = client.services.list()
        for service in services:
            # TODO:
            print(service)
            # service.remove()

    result = ""

    # close connection
    client.close()

    return JSONResponse(content={"result": result, "message": "Success"})
