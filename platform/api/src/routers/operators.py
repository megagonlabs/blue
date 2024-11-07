###### OS / Systems
from curses import noecho
import sys

from fastapi import Depends, Request
import pydash
from constant import BANNED_ENTITY_NAMES, PermissionDenied, account_id_header, acl_enforce

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/operator_registry/")
sys.path.append("./lib/platform/")

###### Parsers, Formats, Utils
import re
import csv
import json
import time
import logging
from utils import json_utils


##### Typing
from pydantic import BaseModel
from typing import Union, Any, Dict, List

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse


###### Schema
class Operator(BaseModel):
    name: str
    description: Union[str, None] = None
    icon: Union[str, dict, None] = None


class Parameter(BaseModel):
    name: str
    description: Union[str, None] = None


JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blueprint import Platform
from operator_registry import OperatorRegistry

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
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{operator_registry_id}", dependencies=[Depends(account_id_header)])

# set logging
logging.getLogger().setLevel("INFO")


write_all_roles = ACL.get_implicit_users_for_permission('operator_registry', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('operator_registry', 'write_own')


def operator_acl_enforce(request: Request, source: dict, write=False, throw=True):
    user_role = request.state.user['role']
    uid = request.state.user['uid']
    allow = False
    if write and user_role in write_all_roles:
        allow = True
    elif write and user_role in write_own_roles:
        if pydash.objects.get(source, 'created_by', None) == uid:
            allow = True
    if throw and not allow:
        raise PermissionDenied
    return allow


#############
@router.get("/operators")
def get_operators(request: Request):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    registry_results = operator_registry.list_records()
    registry_results = list(registry_results.values())
    return JSONResponse(content={"results": registry_results})


@router.get("/operator/{operator_name}")
def get_operator(request: Request, operator_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    result = operator_registry.get_operator(operator_name)
    return JSONResponse(content={"result": result})


@router.post("/operator/{operator_name}")
def add_operator(request: Request, operator_name, operator: Operator):
    operator_db = operator_registry.get_operator(operator_name)
    if operator_name in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": "The name cannot be used."}, status_code=403)
    # if operator already exists, return 409 conflict error
    if not pydash.is_empty(operator_db):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    acl_enforce(request.state.user['role'], 'operator_registry', ['write_all', 'write_own'])
    # TODO: properties
    operator_registry.add_operator(operator_name, request.state.user['uid'], description=operator.description, properties={}, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/operator/{operator_name}")
def update_operator(request: Request, operator_name, operator: Operator):
    operator_db = operator_registry.get_operator(operator_name)
    operator_acl_enforce(request, operator_db, write=True)
    # TODO: properties
    operator_registry.update_operator(operator_name, description=operator.description, icon=operator.icon, properties={}, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/operator/{operator_name}")
def delete_operator(request: Request, operator_name):
    operator_db = operator_registry.get_operator(operator_name)
    operator_acl_enforce(request, operator_db, write=True)
    operator_registry.remove_operator(operator_name, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/operator/{operator_name}/properties")
def get_operator_properties(request: Request, operator_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.get_operator_properties(operator_name)
    return JSONResponse(content={"results": results})


@router.get("/operator/{operator_name}/property/{property_name}")
def get_operator_property(request: Request, operator_name, property_name):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    result = operator_registry.get_operator_property(operator_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/operator/{operator_name}/property/{property_name}")
def set_operator_property(request: Request, operator_name, property_name, property: JSONStructure):
    operator_db = operator_registry.get_operator(operator_name)
    operator_acl_enforce(request, operator_db, write=True)
    operator_registry.set_operator_property(operator_name, property_name, property, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/operator/{operator_name}/property/{property_name}")
def delete_operator_property(request: Request, operator_name, property_name):
    operator_db = operator_registry.get_operator(operator_name)
    operator_acl_enforce(request, operator_db, write=True)
    operator_registry.delete_operator_property(operator_name, property_name, rebuild=True)
    # save
    operator_registry.dump("/blue_data/config/" + operator_registry_id + ".operators.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/operators/search")
def search_operators(request: Request, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    acl_enforce(request.state.user['role'], 'operator_registry', 'read_all')
    results = operator_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})
