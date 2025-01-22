###### OS / Systems
from curses import noecho
import sys

from fastapi import Depends, Request
import pydash
from constant import BANNED_ENTITY_NAMES, PermissionDenied, account_id_header, acl_enforce

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/model_registry/")
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
class Model(BaseModel):
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
from model_registry import ModelRegistry

###### Properties
from settings import ACL, PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
model_registry_id = PROPERTIES["model_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
model_registry = ModelRegistry(id=model_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{model_registry_id}", dependencies=[Depends(account_id_header)])

# set logging
logging.getLogger().setLevel("INFO")


write_all_roles = ACL.get_implicit_users_for_permission('model_registry', 'write_all')
write_own_roles = ACL.get_implicit_users_for_permission('model_registry', 'write_own')


def model_acl_enforce(request: Request, source: dict, write=False, throw=True):
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
@router.get("/models")
def get_models(request: Request):
    acl_enforce(request.state.user['role'], 'model_registry', 'read_all')
    registry_results = model_registry.list_records()
    return JSONResponse(content={"results": registry_results})


@router.get("/model/{model_name}")
def get_model(request: Request, model_name):
    acl_enforce(request.state.user['role'], 'model_registry', 'read_all')
    result = model_registry.get_model(model_name)
    return JSONResponse(content={"result": result})


@router.post("/model/{model_name}")
def add_model(request: Request, model_name, model: Model):
    model_db = model_registry.get_model(model_name)
    if model_name in BANNED_ENTITY_NAMES:
        return JSONResponse(content={"message": "The name cannot be used."}, status_code=403)
    # if model already exists, return 409 conflict error
    if not pydash.is_empty(model_db):
        return JSONResponse(content={"message": "The name already exists."}, status_code=409)
    acl_enforce(request.state.user['role'], 'model_registry', ['write_all', 'write_own'])
    # TODO: properties
    model_registry.add_model(model_name, request.state.user['uid'], description=model.description, properties={}, rebuild=True)
    # save
    model_registry.dump("/blue_data/config/" + model_registry_id + ".models.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/model/{model_name}")
def update_model(request: Request, model_name, model: Model):
    model_db = model_registry.get_model(model_name)
    model_acl_enforce(request, model_db, write=True)
    # TODO: properties
    model_registry.update_model(model_name, description=model.description, icon=model.icon, properties={}, rebuild=True)
    # save
    model_registry.dump("/blue_data/config/" + model_registry_id + ".models.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/model/{model_name}")
def delete_model(request: Request, model_name):
    model_db = model_registry.get_model(model_name)
    model_acl_enforce(request, model_db, write=True)
    model_registry.remove_model(model_name, rebuild=True)
    # save
    model_registry.dump("/blue_data/config/" + model_registry_id + ".models.json")
    return JSONResponse(content={"message": "Success"})


##### properties
@router.get("/model/{model_name}/properties")
def get_model_properties(request: Request, model_name):
    acl_enforce(request.state.user['role'], 'model_registry', 'read_all')
    results = model_registry.get_model_properties(model_name)
    return JSONResponse(content={"results": results})


@router.get("/model/{model_name}/property/{property_name}")
def get_model_property(request: Request, model_name, property_name):
    acl_enforce(request.state.user['role'], 'model_registry', 'read_all')
    result = model_registry.get_model_property(model_name, property_name)
    return JSONResponse(content={"result": result})


@router.post("/model/{model_name}/property/{property_name}")
def set_model_property(request: Request, model_name, property_name, property: JSONStructure):
    model_db = model_registry.get_model(model_name)
    model_acl_enforce(request, model_db, write=True)
    model_registry.set_model_property(model_name, property_name, property, rebuild=True)
    # save
    model_registry.dump("/blue_data/config/" + model_registry_id + ".models.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/model/{model_name}/property/{property_name}")
def delete_model_property(request: Request, model_name, property_name):
    model_db = model_registry.get_model(model_name)
    model_acl_enforce(request, model_db, write=True)
    model_registry.delete_model_property(model_name, property_name, rebuild=True)
    # save
    model_registry.dump("/blue_data/config/" + model_registry_id + ".models.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/models/search")
def search_models(request: Request, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    acl_enforce(request.state.user['role'], 'model_registry', 'read_all')
    results = model_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})
