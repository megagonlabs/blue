###### OS / Systems
from curses import noecho
import sys

from fastapi import Request
import pydash
from constant import PermissionDenied, acl_enforce

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/data_registry/")
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
class Data(BaseModel):
    name: str
    description: Union[str, None] = None
    icon: Union[str, dict, None] = None


JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blueprint import Platform
from data_registry import DataRegistry

###### Properties
from settings import ACL, PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
data_registry_id = PROPERTIES["data_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
data_registry = DataRegistry(id=data_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{data_registry_id}/data")

# set logging
logging.getLogger().setLevel("INFO")


write_all_roles = ACL.get_implicit_users_for_permission('data_registry', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('data_registry', 'write_own')


def source_acl_enforce(request: Request, source: dict, write=False, throw=True):
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
@router.get("/")
def get_data(request: Request):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    results = data_registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/search")
def search_data(request: Request, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    results = data_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})


@router.get("/{source_name}")
def get_data_source(request: Request, source_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    result = data_registry.get_source(source_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}")
def add_source(request: Request, source_name, data: Data):
    source_db = data_registry.get_source(source_name)
    # if source already exists, return 409 conflict error
    if not pydash.is_empty(source_db):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    acl_enforce(request.state.user['role'], 'data_registry', ['write_all', 'write_own'])
    # TODO: properties
    data_registry.register_source(source_name, request.state.user['uid'], description=data.description, properties={}, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}")
def update_source(request: Request, source_name, data: Data, sync: bool = False, recursive: bool = False):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    # TODO: properties
    data_registry.update_source(source_name, description=data.description, icon=data.icon, properties={}, rebuild=True)
    if sync:
        data_registry.sync_source(source_name, recursive=recursive, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}")
def delete_source(request: Request, source_name):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    data_registry.deregister_source(source_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/{source_name}/properties")
def get_source_properties(request: Request, source_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    results = data_registry.get_source_properties(source_name)
    return JSONResponse(content={"results": results})


@router.get("/{source_name}/property/{property_name}")
def get_source_property(request: Request, source_name, property_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    result = data_registry.get_source_property(source_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}/property/{property_name}")
def set_source_property(request: Request, source_name, property_name, property: JSONStructure):
    source_db = data_registry.get_source(source_name)
    source_acl_enforce(request, source_db, write=True)
    data_registry.set_source_property(source_name, property_name, property, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}/property/{property_name}")
def delete_source_property(request: Request, source_name, property_name):
    source_db = data_registry.get_source(source_name)
    source_acl_enforce(request, source_db, write=True)
    data_registry.delete_source_property(source_name, property_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/{source_name}/databases")
def get_data_source_databases(request: Request, source_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    results = data_registry.get_source_databases(source_name)
    return JSONResponse(content={"results": results})


@router.get("/{source_name}/database/{database_name}")
def get_data_source_database(request: Request, source_name, database_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    result = data_registry.get_source_database(source_name, database_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}/database/{database_name}")
def add_data_source_database(request: Request, source_name, database_name, data: Data):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    # TODO: properties
    data_registry.register_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}/database/{database_name}")
def update_source_database(request: Request, source_name, database_name, data: Data, sync: bool = False, recursive: bool = False):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    # TODO: properties
    data_registry.update_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
    if sync:
        data_registry.sync_source_database(source_name, database_name, recursive=recursive, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}/database/{database_name}")
def delete_source_database(request: Request, source_name, database_name):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    data_registry.deregister_source_database(source_name, database_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/{source_name}/database/{database_name}/collections")
def get_data_source_database_collections(request: Request, source_name, database_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    results = data_registry.get_source_database_collections(source_name, database_name)
    return JSONResponse(content={"results": results})


@router.get("/{source_name}/database/{database_name}/collection/{collection_name}")
def get_data_source_database_collection(request: Request, source_name, database_name, collection_name):
    acl_enforce(request.state.user['role'], 'data_registry', 'read_all')
    result = data_registry.get_source_database_collection(source_name, database_name, collection_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}/database/{database_name}/collection/{collection_name}")
def add_data_source_database_collection(request: Request, source_name, database_name, collection_name, data: Data):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    # TODO: properties
    data_registry.register_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}/database/{database_name}/collection/{collection_name}")
def update_source_database_collection(request: Request, source_name, database_name, collection_name, data: Data, sync: bool = False, recursive: bool = False):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    # TODO: properties
    data_registry.update_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
    if sync:
        data_registry.sync_source_database_collection(source_name, database_name, collection_name, recursive=recursive, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}/database/{database_name}/collection/{collection_name}")
def delete_source_database_collection(request: Request, source_name, database_name, collection_name):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    data_registry.deregister_source_database_collection(source_name, database_name, collection_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


### sync entities
@router.put('/{source_name}/sync')
def sync_source(request: Request, source_name, recursive: bool = False):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    data_registry.sync_source(source_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}/database/{database_name}/sync")
def sync_source_database(request: Request, source_name, database_name, recursive: bool = False):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    data_registry.sync_source_database(source_name, database_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}/database/{database_name}/collection/{collection_name}/sync")
def sync_source_database_collection(request: Request, source_name, database_name, collection_name, recursive: bool = False):
    source = data_registry.get_source(source_name)
    source_acl_enforce(request, source, write=True)
    data_registry.sync_source_database_collection(source_name, database_name, collection_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={"message": "Success"})
