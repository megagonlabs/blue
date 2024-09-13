###### OS / Systems
from curses import noecho
import sys

from fastapi import Request
import pydash
from constant import PermissionDenied, acl_enforce

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/platform/")


###### Parsers, Formats, Utils
import json
import logging
from utils import json_utils

###### Docker
import docker

##### Typing
from typing import Union, Any, Dict, List

###### FastAPI, Web, Auth
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
from settings import ACL, PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'


###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)


##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/containers")

# set logging
logging.getLogger().setLevel("INFO")

write_all_roles = ACL.get_implicit_users_for_permission('platform_agents', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('platform_agents', 'write_own')
read_all_roles = ACL.get_implicit_users_for_permission('platform_agents', 'read_all')
read_own_roles = ACL.get_implicit_users_for_permission('platform_agents', 'read_own')


def container_acl_enforce(request: Request, agent: dict, read=False, write=False, throw=True):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    allow = False
    if (read and user_role in read_all_roles) or (write and user_role in write_all_roles):
        allow = True
    elif (read and user_role in read_own_roles) and (write and user_role in write_own_roles):
        if pydash.objects.get(agent, 'created_by', None) == uid:
            allow = True
    if throw and not allow:
        raise PermissionDenied
    return allow

### AGENTS
@router.get("/agents/")
# get the list of agent running agents on the platform
def list_agent_containers(request: Request):
    acl_enforce(request.state.user['role'], 'platform_agents', ['read_all', 'read_own'])
    # connect to docker
    client = docker.from_env()
    results = []
    # get list of docker containers based on deploy target
    if PROPERTIES["platform.deploy.target"] == "localhost":
        containers = client.containers.list()
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
    temp = []
    for container in results:
        agent = agent_registry.get_agent(container['agent'])
        if container_acl_enforce(request, agent, read=True, throw=False):
            temp.append(container)
    return JSONResponse(content={"results": temp})


@router.post("/agents/agent/{agent_name}")
# deploy an agent container with the name {agent_name} to the agent registry with the name
def deploy_agent_container(request: Request, agent_name):
    agent = agent_registry.get_agent(agent_name)
    container_acl_enforce(request, agent, write=True)
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
            "--serve " + agent_name + " " + "--platform " + platform_id + " " + "--registry " + agent_registry_id + " " + "--properties " + "'" + json.dumps(agent_properties) + "'",
            network="blue_platform_" + PROPERTIES["platform.name"] + "_network_bridge",
            name="blue_agent_" + platform_id + "_" + agent_registry_id + "_" + agent_name.lower(),
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
            name="blue_agent_" + platform_id + "_" + agent_registry_id + "_" + agent_name.lower(),
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
def update_agent_container(request: Request, agent_name):
    agent = agent_registry.get_agent(agent_name)
    container_acl_enforce(request, agent, write=True)
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
def shutdown_agent_container(request: Request, agent_name):
    agent = agent_registry.get_agent(agent_name)
    container_acl_enforce(request, agent, write=True)

    # connect to docker
    client = docker.from_env()

    if PROPERTIES["platform.deploy.target"] == "localhost":
        containers = client.containers.list()
        for container in containers:
            h = container.attrs["Config"]["Hostname"]
            if h.find("blue_agent") < 0:
                continue
            hs = h.split("_")
            a = hs[3]
            if a == agent_name:
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


## SERVICES
@router.get("/services/")
# get the list of services running on the platform
def list_service_containers(request: Request):
    #TODO: 
    #acl_enforce(request.state.user['role'], 'platform_services', ['read_all', 'read_own'])

    # connect to docker
    client = docker.from_env()
    results = []
    # get list of docker containers based on deploy target
    if PROPERTIES["platform.deploy.target"] == "localhost":
        containers = client.containers.list()
        for container in containers:
            c = {}
            c["id"] = container.attrs["Id"]
            c["hostname"] = container.attrs["Config"]["Hostname"]
            c["created_date"] = container.attrs["Created"]
            c["image"] = container.attrs["Config"]["Image"]
            c["status"] = container.attrs["State"]["Status"]
            labels = container.attrs["Config"]["Labels"]
            if 'blue.agent' in labels:
                l = labels['blue.service']
                la = l.split(".")
                c["service"] = la[1]
                c["platform"] = la[0]
                if c["platform"] == platform_id:
                    results.append(c)
    elif PROPERTIES["platform.deploy.target"] == "swarm":
        services = client.services.list()
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
            if 'blue.service' in labels:
                l = labels['blue.service']
                la = l.split(".")
                c["service"] = la[1]
                c["platform"] = la[0]
                if c["platform"] == platform_id:
                    results.append(c)

    # close connection
    client.close()
    temp = []
    for container in results:
        agent = agent_registry.get_agent(container['agent'])
        if container_acl_enforce(request, agent, read=True, throw=False):
            temp.append(container)
    return JSONResponse(content={"results": temp})


@router.delete("/services/service/{service_name}")
# shutdown the service container with the name {service_name} 
def shutdown_service_container(request: Request, service_name):
    #TODO:
    #container_acl_enforce(request, service_name, write=True)

    # connect to docker
    client = docker.from_env()

    if PROPERTIES["platform.deploy.target"] == "localhost":
        containers = client.containers.list()
        for container in containers:
            h = container.attrs["Config"]["Hostname"]
            if h.find("blue_service") < 0:
                continue
            hs = h.split("_")
            s = hs[3]
            if s == service_name:
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