###### OS / Systems
from curses import noecho

from fastapi import Depends, Request
import pydash

from constant import BANNED_ENTITY_NAMES, PermissionDenied, account_id_header, acl_enforce


###### Parsers, Formats, Utils
import logging

###### Docker
import docker

##### Typing
from pydantic import BaseModel
from typing import Union, Any, Dict, List

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse


###### Schema
class AgentGroupSchema(BaseModel):
    name: str
    description: Union[str, None] = None
    icon: Union[str, dict, None] = None


class AgentSchema(BaseModel):
    name: str
    description: Union[str, None] = None
    icon: Union[str, dict, None] = None


class ParameterSchema(BaseModel):
    name: str
    description: Union[str, None] = None


JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blue.agent import Agent
from blue.platform import Platform
from blue.agents.registry import AgentRegistry


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
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{agent_registry_id}", dependencies=[Depends(account_id_header)])

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
                name = name.split(Agent.SEPARATOR)[0]
                if name in containers:
                    registry_result['container'] = containers[name]
                else:
                    registry_result['container'] = {"status": "not exist"}

    return registry_results


write_all_roles = ACL.get_implicit_users_for_permission('agent_registry', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('agent_registry', 'write_own')


def agent_acl_enforce(request: Request, agent: dict, write=False, throw=True):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    allow = False
    if write and user_role in write_all_roles:
        allow = True
    elif write and user_role in write_own_roles:
        if pydash.objects.get(agent, 'created_by', None) == uid:
            allow = True
    if throw and not allow:
        raise PermissionDenied
    return allow


def agent_group_acl_enforce(request: Request, agent_group: dict, write=False, throw=True):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    allow = False
    if write and user_role in write_all_roles:
        allow = True
    elif write and user_role in write_own_roles:
        if pydash.objects.get(agent_group, 'created_by', None) == uid:
            allow = True
    if throw and not allow:
        raise PermissionDenied
    return allow


#############
@router.get("/agents")
def get_agents(request: Request, recursive: bool = False):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    # get base agents
    results = []
    base_agents = agent_registry.list_records(type="agent", recursive=False)
    results.extend(base_agents)
    if recursive:
        # get derived agents
        derived_agents = agent_registry.list_records(condition='[?(@.type=="agent")]..[?(@.type=="agent")]')
        results.extend(derived_agents)

    merged_results = merge_container_results(results)
    return JSONResponse(content={"results": merged_results})


@router.get("/agent/{agent_name}")
@router.get("/agent/{path:path}/agent/{agent_name}")
@router.get('/agent_group/{agent_group}/agent/{agent_name}')
@router.get('/agent_group/{agent_group}/agent/{path:path}/agent/{agent_name}')
def get_agent(request: Request, agent_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent(agent_name)
    merged_results = merge_container_results([result])
    return JSONResponse(content={"result": merged_results[0]})


@router.post("/agent/{agent_name}")
def add_agent(request: Request, agent_name, agent: AgentSchema):
    agent_db = agent_registry.get_agent(agent_name)
    if agent_registry._extract_shortname(agent_name) in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": "The name cannot be used."}, status_code=403)
    # if agent already exists, return 409 conflict error
    if not pydash.is_empty(agent_db):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    acl_enforce(request.state.user['role'], 'agent_registry', ['write_all', 'write_own'])
    # TODO: properties
    agent_registry.add_agent(agent_name, request.state.user['uid'], description=agent.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/agent/{agent_name}")
def update_agent(request: Request, agent_name, agent: AgentSchema):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    # TODO: properties
    agent_registry.update_agent(agent_name, description=agent.description, icon=agent.icon, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent/{agent_name}")
def delete_agent(request: Request, agent_name):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.remove_agent(agent_name, rebuild=True)
    # remove agent from agent groups
    agent_groups = agent_registry.get_agent_groups()
    for group in agent_groups:
        agent_registry.remove_agent_from_agent_group(group['name'], agent_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/agent/{agent_name}/properties")
def get_agent_properties(request: Request, agent_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_properties(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/agent/{agent_name}/property/{property_name}")
def get_agent_property(request: Request, agent_name, property_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_property(agent_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/agent/{agent_name}/property/{property_name}")
def set_agent_property(request: Request, agent_name, property_name, property: JSONStructure):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.set_agent_property(agent_name, property_name, pydash.objects.get(property, [property_name], None), rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent/{agent_name}/property/{property_name}")
def delete_agent_property(request: Request, agent_name, property_name):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.delete_agent_property(agent_name, property_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


##### inputs
@router.get("/agent/{agent_name}/inputs")
def get_agent_inputs(request: Request, agent_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_inputs(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/agent/{agent_name}/input/{param_name}")
@router.get("/agent/{path:path}/agent/{agent_name}/input/{param_name}")
@router.get("/agent_group/{agent_group}/agent/{agent_name}/input/{param_name}")
@router.get("/agent_group/{agent_group}/agent/{path:path}/agent/{agent_name}/input/{param_name}")
def get_agent_input(request: Request, agent_name, param_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_input(agent_name, param_name)
    return JSONResponse(content={"result": result})


@router.post("/agent/{agent_name}/input/{param_name}")
def add_agent_input(request: Request, agent_name, param_name, parameter: ParameterSchema):
    input = agent_registry.get_agent_input(agent_name, param_name)
    output = agent_registry.get_agent_output(agent_name, param_name)
    if agent_registry._extract_shortname(param_name) in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": "The name cannot be used."}, status_code=403)
    # if name already exists, return 409 conflict error
    if not pydash.is_empty(input) or not pydash.is_empty(output):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    # TODO: properties
    agent_registry.add_agent_input(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/agent/{agent_name}/input/{param_name}")
def update_agent_input(request: Request, agent_name, param_name, parameter: ParameterSchema):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    # TODO: properties
    agent_registry.update_agent_input(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent/{agent_name}/input/{param_name}")
@router.delete("/agent/{path:path}/agent/{agent_name}/input/{param_name}")
@router.delete("/agent_group/{agent_group}/agent/{agent_name}/input/{param_name}")
@router.delete("/agent_group/{agent_group}/agent/{path:path}/agent/{agent_name}/input/{param_name}")
def delete_agent_input(request: Request, agent_name, param_name):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.del_agent_input(agent_name, param_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/agent/{agent_name}/input/{param_name}/properties")
def get_agent_input_properties(request: Request, agent_name, param_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_input_properties(agent_name, param_name)
    return JSONResponse(content={"results": results})


@router.get("/agent/{agent_name}/input/{param_name}/property/{property_name}")
def get_agent_input_property(request: Request, agent_name, param_name, property_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_input_property(agent_name, param_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/agent/{agent_name}/input/{param_name}/property/{property_name}")
def set_agent_input_property(request: Request, agent_name, param_name, property_name, property: JSONStructure):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.set_agent_input_property(agent_name, param_name, property_name, pydash.objects.get(property, [property_name], None), rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent/{agent_name}/input/{param_name}/property/{property_name}")
def delete_agent_input_property(request: Request, agent_name, param_name, property_name):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.delete_agent_input_property(agent_name, param_name, property_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


##### outputs
@router.get("/agent/{agent_name}/outputs")
def get_agent_outputs(request: Request, agent_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_outputs(agent_name)
    return JSONResponse(content={"results": results})


@router.get("/agent/{agent_name}/output/{param_name}")
@router.get("/agent/{path:path}/agent/{agent_name}/output/{param_name}")
@router.get("/agent_group/{agent_group}/agent/{agent_name}/output/{param_name}")
@router.get("/agent_group/{agent_group}/agent/{path:path}/agent/{agent_name}/output/{param_name}")
def get_agent_output(request: Request, agent_name, param_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_output(agent_name, param_name)
    return JSONResponse(content={"result": result})


@router.post("/agent/{agent_name}/output/{param_name}")
def add_agent_output(request: Request, agent_name, param_name, parameter: ParameterSchema):
    input = agent_registry.get_agent_input(agent_name, param_name)
    output = agent_registry.get_agent_output(agent_name, param_name)
    if agent_registry._extract_shortname(param_name) in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": "The name cannot be used."}, status_code=403)
    # if name already exists, return 409 conflict error
    if not pydash.is_empty(input) or not pydash.is_empty(output):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    # TODO: properties
    agent_registry.add_agent_output(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.put("/agent/{agent_name}/output/{param_name}")
def update_agent_output(request: Request, agent_name, param_name, parameter: ParameterSchema):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    # TODO: properties
    agent_registry.update_agent_output(agent_name, param_name, description=parameter.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent/{agent_name}/output/{param_name}")
@router.delete("/agent/{path:path}/agent/{agent_name}/output/{param_name}")
@router.delete("/agent_group/{agent_group}/agent/{agent_name}/output/{param_name}")
@router.delete("/agent_group/{agent_group}/agent/{path:path}/agent/{agent_name}/output/{param_name}")
def delete_agent_output(request: Request, agent_name, param_name):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.del_agent_output(agent_name, param_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/agent/{agent_name}/output/{param_name}/properties")
def get_agent_output_properties(request: Request, agent_name, param_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_output_properties(agent_name, param_name)
    return JSONResponse(content={"results": results})


@router.get("/agent/{agent_name}/output/{param_name}/property/{property_name}")
def get_agent_output_property(request: Request, agent_name, param_name, property_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_output_property(agent_name, param_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/agent/{agent_name}/output/{param_name}/property/{property_name}")
def set_agent_output_property(request: Request, agent_name, param_name, property_name, property: JSONStructure):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.set_agent_output_property(agent_name, param_name, property_name, pydash.objects.get(property, [property_name], None), rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent/{agent_name}/output/{param_name}/property/{property_name}")
def delete_agent_output_property(request: Request, agent_name, param_name, property_name):
    agent_db = agent_registry.get_agent(agent_name)
    agent_acl_enforce(request, agent_db, write=True)
    agent_registry.delete_agent_output_property(agent_name, param_name, property_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/agents/search")
def search_agents(request: Request, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})


##### derived agents
@router.get("/agent/{agent_name}/agents")
def get_agent_derived_agents(request: Request, agent_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_derived_agents(agent_name)
    return JSONResponse(content={"results": results})


#############
# agent groups
@router.get("/agent_groups")
def get_agent_groups(request: Request):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    registry_results = agent_registry.get_agent_groups()
    if registry_results is None:
        registry_results = []
    return JSONResponse(content={"results": registry_results})


@router.get("/agent_group/{group_name}")
def get_agent_group(request: Request, group_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_group(group_name)
    return JSONResponse(content={"result": result})


@router.put("/agent_group/{group_name}")
def update_agent_group(request: Request, group_name, group: AgentGroupSchema):
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    # TODO: properties
    agent_registry.update_agent_group(group_name, description=group.description, icon=group.icon, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete('/agent_group/{group_name}')
def delete_agent_group(request: Request, group_name):
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    agent_registry.remove_agent_group(group_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.post("/agent_group/{group_name}")
def add_agent_group(request: Request, group_name, group: AgentGroupSchema):
    agent_group_db = agent_registry.get_agent_group(group_name)
    if agent_registry._extract_shortname(group_name) in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": "The name cannot be used."}, status_code=403)
    # if agent already exists, return 409 conflict error
    if not pydash.is_empty(agent_group_db):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    acl_enforce(request.state.user['role'], 'agent_registry', ['write_all', 'write_own'])
    # TODO: properties
    agent_registry.add_agent_group(group_name, request.state.user['uid'], description=group.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/agent_group/{group_name}/agents")
def get_agent_group_agents(request: Request, group_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_group_agents(group_name)
    if results is None:
        results = []
    return JSONResponse(content={"results": results})


@router.post("/agent_group/{group_name}/agent/{agent_name}")
def add_agent_to_agent_group(request: Request, group_name, agent_name, agent: AgentSchema):
    agent_existing = agent_registry.get_agent_group_agent(group_name, agent_name)
    if agent_registry._extract_shortname(agent_name) in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": f"\"{agent_name}\" cannot be used."}, status_code=403)
    # if name already exists, return 409 conflict error
    if not pydash.is_empty(agent_existing):
        return JSONResponse(content={"message": f"\"{agent_name}\" already exists."}, status_code=409)
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    # TODO: properties
    agent_registry.add_agent_to_agent_group(group_name, agent_name, description=agent.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/agent_group/{group_name}/agent/{agent_name}")
def update_agent_in_agent_group(request: Request, group_name, agent_name, agent: AgentSchema):
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    # TODO: properties
    agent_registry.update_agent_in_agent_group(group_name, agent_name, description=agent.description, properties={}, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent_group/{group_name}/agent/{agent_name}")
def delete_agent_from_agent_group(request: Request, group_name, agent_name):
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    agent_registry.remove_agent_from_agent_group(group_name, agent_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/agent_group/{group_name}/agent/{agent_name}/properties")
def get_agent_properties_in_agent_group(request: Request, group_name, agent_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    results = agent_registry.get_agent_group_agent_properties(group_name, agent_name)
    return JSONResponse(content={"results": results})


@router.get("/agent_group/{group_name}/agent/{agent_name}/property/{property_name}")
def get_agent_property_in_agent_group(request: Request, group_name, agent_name, property_name):
    acl_enforce(request.state.user['role'], 'agent_registry', 'read_all')
    result = agent_registry.get_agent_property_in_agent_group(group_name, agent_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/agent_group/{group_name}/agent/{agent_name}/property/{property_name}")
def set_agent_property_in_agent_group(request: Request, group_name, agent_name, property_name, property: JSONStructure):
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    agent_registry.set_agent_property_in_agent_group(group_name, agent_name, property_name, pydash.objects.get(property, [property_name], None), rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/agent_group/{group_name}/agent/{agent_name}/property/{property_name}")
def delete_agent_property_in_agent_group(request: Request, group_name, agent_name, property_name):
    agent_group_db = agent_registry.get_agent_group(group_name)
    agent_group_acl_enforce(request, agent_group_db, write=True)
    agent_registry.delete_agent_property_in_agent_group(group_name, agent_name, property_name, rebuild=True)
    # save
    agent_registry.dump("/blue_data/config/" + agent_registry_id + ".agents.json")
    return JSONResponse(content={"message": "Success"})
