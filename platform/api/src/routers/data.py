###### OS / Systems
from curses import noecho
import sys

from fastapi import Request

from constant import authorize

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/data_registry/")
sys.path.append("./lib/platform/")

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


JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from session import Session
from blueprint import Platform
from data_registry import DataRegistry

###### Properties
from settings import PROPERTIES

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


#############
@router.get("/")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data(request: Request):
    results = data_registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/sources")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data_sources(request: Request):
    results = data_registry.get_sources()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{source_name}")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data_source(request: Request, source_name):
    result = data_registry.get_source(source_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}")
@authorize(roles=['admin'])
def add_source(request: Request, source_name, data: Data):
    # TODO: properties
    data_registry.register_source(source_name, description=data.description, properties={}, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}")
@authorize(roles=['admin'])
def update_source(request: Request, source_name, data: Data, sync: bool = False, recursive: bool = False):
    # TODO: properties
    data_registry.update_source(source_name, description=data.description, properties={}, rebuild=True)
    if sync:
        data_registry.sync_source(source_name, recursive=recursive, rebuild=True)

    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}")
@authorize(roles=['admin'])
def delete_source(request: Request, source_name):
    data_registry.deregister_source(source_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/{source_name}/databases")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data_source_databases(request: Request, source_name):
    results = data_registry.get_source_databases(source_name)
    return JSONResponse(content={"results": results})


@router.get("/{source_name}/database/{database_name}")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data_source_database(request: Request, source_name, database_name):
    result = data_registry.get_source_database(source_name, database_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}/database/{database_name}")
@authorize(roles=['admin'])
def add_data_source_database(request: Request, source_name, database_name, data: Data):
    # TODO: properties
    data_registry.register_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}/database/{database_name}")
@authorize(roles=['admin'])
def update_source_database(request: Request, source_name, database_name, data: Data, sync: bool = False, recursive: bool = False):
    # TODO: properties
    data_registry.update_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
    if sync:
        data_registry.sync_source_database(source_name, database_name, recursive=recursive, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}/database/{database_name}")
@authorize(roles=['admin'])
def delete_source_database(request: Request, source_name, database_name):
    data_registry.deregister_source_database(source_name, database_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/{source_name}/database/{database_name}/collections")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data_source_database_collections(request: Request, source_name, database_name):
    results = data_registry.get_source_database_collections(source_name, database_name)
    return JSONResponse(content={"results": results})


@router.get("/{source_name}/database/{database_name}/collection/{collection_name}")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def get_data_source_database_collection(request: Request, source_name, database_name, collection_name):
    result = data_registry.get_source_database_collection(source_name, database_name, collection_name)
    return JSONResponse(content={"result": result})


@router.post("/{source_name}/database/{database_name}/collection/{collection_name}")
@authorize(roles=['admin'])
def add_data_source_database_collection(request: Request, source_name, database_name, collection_name, data: Data):
    # TODO: properties
    data_registry.register_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.put("/{source_name}/database/{database_name}/collection/{collection_name}")
@authorize(roles=['admin'])
def update_source_database_collection(request: Request, source_name, database_name, collection_name, data: Data, sync: bool = False, recursive: bool = False):
    # TODO: properties
    data_registry.update_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
    if sync:
        data_registry.sync_source_database_collection(source_name, database_name, collection_name, recursive=recursive, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.delete("/{source_name}/database/{database_name}/collection/{collection_name}")
@authorize(roles=['admin'])
def delete_source_database_collection(request: Request, source_name, database_name, collection_name):
    data_registry.deregister_source_database_collection(source_name, database_name, collection_name, rebuild=True)
    # save
    data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
    return JSONResponse(content={"message": "Success"})


@router.get("/search")
@authorize(roles=['admin', 'member', 'developer', 'guest'])
def search_data(request: Request, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    results = data_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={"results": results})
