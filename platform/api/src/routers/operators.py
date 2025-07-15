###### OS / Systems
from curses import noecho
import sys

from fastapi import Depends, Request
import pydash
from constant import PermissionDenied, account_id_header, acl_enforce

###### Parsers, Formats, Utils
import re
import csv
import json
import time
import logging


##### Typing
from pydantic import BaseModel
from typing import Union, Any, Dict, List

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse


###### Schema
class OperatorSchema(BaseModel):
    name: str
    description: Union[str, None] = None
    icon: Union[str, dict, None] = None


JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blue.platform import Platform
from blue.operators.registry import OperatorRegistry

###### Properties
from settings import ACL, PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
operator_registry_id = PROPERTIES["operator_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
operator_registry = OperatorRegistry(id=operator_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{operator_registry_id}/operators", dependencies=[Depends(account_id_header)])

# set logging
logging.getLogger().setLevel("INFO")


write_all_roles = ACL.get_implicit_users_for_permission('operator_registry', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('operator_registry', 'write_own')


def server_acl_enforce(request: Request, server: dict, write=False, throw=True):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    allow = False
    if write and user_role in write_all_roles:
        allow = True
    elif write and user_role in write_own_roles:
        if pydash.objects.get(server, 'created_by', None) == uid:
            allow = True
    if throw and not allow:
        raise PermissionDenied
    return allow


#############
@router.get("/")
def get_operators(request: Request):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.list_records()
    return JSONResponse(content={"results": results})


@router.get("/search")
def search_operators(request: Request, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})


@router.get("/{server_name}")
def get_server(request: Request, server_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    result = operator_registry.get_server(server_name)
    return JSONResponse(content={"result": result})


@router.post("/{server_name}")
def add_server(request: Request, server_name, data: OperatorSchema):
    server = operator_registry.get_server(server_name)
    # if server already exists, return 409 conflict error
    if not pydash.is_empty(server):
        return JSONResponse(content={"message": f"\"{server_name}\" already exists"}, status_code=409)
    acl_enforce(request.state.user['role'], 'operator_registry', ['write_all', 'write_own'])
    # TODO: properties
    operator_registry.register_server(server_name, request.state.user['uid'], description=data.description, properties={}, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{server_name}")
def update_server(request: Request, server_name, data: OperatorSchema, sync: bool = False, recursive: bool = False):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    # TODO: properties
    operator_registry.update_server(server_name, description=data.description, icon=data.icon, properties={}, rebuild=True)
    if sync:
        operator_registry.sync_server(server_name, recursive=recursive, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{server_name}")
def delete_server(request: Request, server_name):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    operator_registry.deregister_server(server_name, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/{server_name}/properties")
def get_server_properties(request: Request, server_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.get_server_properties(server_name)
    return JSONResponse(content={"results": results})


@router.get("/{server_name}/property/{property_name}")
def get_server_property(request: Request, server_name, property_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    result = operator_registry.get_server_property(server_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/{server_name}/property/{property_name}")
def set_server_property(request: Request, server_name, property_name, property: JSONStructure):
    server_db = operator_registry.get_server(server_name)
    server_acl_enforce(request, server_db, write=True)
    operator_registry.set_server_property(server_name, property_name, pydash.objects.get(property, [property_name], None), rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{server_name}/property/{property_name}")
def delete_server_property(request: Request, server_name, property_name):
    server_db = operator_registry.get_server(server_name)
    server_acl_enforce(request, server_db, write=True)
    operator_registry.delete_server_property(server_name, property_name, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/{server_name}/operators")
def get_server_operators(request: Request, server_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.get_server_operators(server_name)
    return JSONResponse(content={"results": results})


@router.get("/{server_name}/operator/{operator_name}")
def get_server_operator(request: Request, server_name, operator_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    result = operator_registry.get_server_operator(server_name, operator_name)
    return JSONResponse(content={"result": result})


@router.post("/{server_name}/operator/{operator_name}")
def add_server_operator(request: Request, server_name, operator_name, data: OperatorSchema):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    # TODO: properties
    operator_registry.register_server_operator(server_name, operator_name, description=data.description, properties={}, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{server_name}/operator/{operator_name}")
def update_server_operator(request: Request, server_name, operator_name, data: OperatorSchema, sync: bool = False, recursive: bool = False):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    # TODO: properties
    operator_registry.update_server_operator(server_name, operator_name, description=data.description, properties={}, rebuild=True)
    if sync:
        operator_registry.sync_server_operator(server_name, operator_name, recursive=recursive, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{server_name}/operator/{operator_name}")
def delete_server_operator(request: Request, server_name, operator_name):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    operator_registry.deregister_server_operator(server_name, operator_name, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/{server_name}/operator/{operator_name}/properties")
def get_server_operator_properties(request: Request, server_name, operator_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.get_server_operator_properties(server_name, operator_name)
    return JSONResponse(content={"results": results})


@router.get("/{server_name}/operator/{operator_name}/property/{property_name}")
def get_server_operator_property(request: Request, server_name, operator_name, property_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    result = operator_registry.get_server_operator_property(server_name, operator_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/{server_name}/operator/{operator_name}/property/{property_name}")
def set_server_operator_property(request: Request, server_name, operator_name, property_name, property: JSONStructure):
    server_db = operator_registry.get_server(server_name)
    server_acl_enforce(request, server_db, write=True)
    operator_registry.set_server_operator_property(server_name, operator_name, property_name, pydash.objects.get(property, [property_name], None), rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{server_name}/operator/{operator_name}/property/{property_name}")
def delete_server_operator_property(request: Request, server_name, operator_name, property_name):
    server_db = operator_registry.get_server(server_name)
    server_acl_enforce(request, server_db, write=True)
    operator_registry.delete_server_operator_property(server_name, operator_name, property_name, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


### sync entities
@router.put('/{server_name}/sync')
def sync_server(request: Request, server_name, recursive: bool = False):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    operator_registry.sync_server(server_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.put("/{server_name}/operator/{operator_name}/sync")
def sync_server_operator(request: Request, server_name, operator_name, recursive: bool = False):
    server = operator_registry.get_server(server_name)
    server_acl_enforce(request, server, write=True)
    operator_registry.sync_server_operator(server_name, operator_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={"message": "Success"})
