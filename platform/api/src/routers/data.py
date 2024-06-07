###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/data_registry/")
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

###### FastAPI
from APIRouter import APIRouter
from fastapi.responses import JSONResponse
from typing import Union, Any, Dict, AnyStr, List
from pydantic import BaseModel, Json
from server import PLATFORM_PREFIX


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
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
data_registry_id = PROPERTIES["data_registry.name"]

###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
data_registry = DataRegistry(id=data_registry_id, prefix=prefix, properties=PROPERTIES)

##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/registry/{data_registry_id}/data")

#############
@router.get("/")
def get_data():
    results = data_registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/sources")
def get_data_sources(registry_name):
    if registry_name == data_registry_id:
        results = data_registry.get_sources()
        return JSONResponse(content={"results": list(results.values())})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.get("/source/{source_name}")
def get_data_source(registry_name, source_name):
    if registry_name == data_registry_id:
        result = data_registry.get_source(source_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.post("/source/{source_name}")
def add_source(registry_name, source_name, data: Data):
    if registry_name == data_registry_id:
        # TODO: properties
        data_registry.register_source(source_name, description=data.description, properties={}, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.put("/source/{source_name}")
def update_source(registry_name, source_name, data: Data, sync: bool = False, recursive: bool = False):
    if registry_name == data_registry_id:
        # TODO: properties
        data_registry.update_source(source_name, description=data.description, properties={}, rebuild=True)
        if sync:
            data_registry.sync_source(source_name, recursive=recursive, rebuild=True)

        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.delete("/source/{source_name}")
def delete_source(registry_name, source_name):
    if registry_name == data_registry_id:
        data_registry.deregister_source(source_name, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.get("/source/{source_name}/databases")
def get_data_source_databases(registry_name, source_name):
    if registry_name == data_registry_id:
        results = data_registry.get_source_databases(source_name)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.get("/source/{source_name}/database/{database_name}")
def get_data_source_database(registry_name, source_name, database_name):
    if registry_name == data_registry_id:
        result = data_registry.get_source_database(source_name, database_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.post("/source/{source_name}/database/{database_name}")
def add_data_source_database(registry_name, source_name, database_name, data: Data):
    if registry_name == data_registry_id:
        # TODO: properties
        data_registry.register_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.put("/source/{source_name}/database/{database_name}")
def update_source_database(registry_name, source_name, database_name, data: Data, sync: bool = False, recursive: bool = False):
    if registry_name == data_registry_id:
        # TODO: properties
        data_registry.update_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
        if sync:
            data_registry.sync_source_database(source_name, database_name, recursive=recursive, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.delete("/source/{source_name}/database/{database_name}")
def delete_source_database(registry_name, source_name, database_name):
    if registry_name == data_registry_id:
        data_registry.deregister_source_database(source_name, database_name, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.get("/source/{source_name}/database/{database_name}/collections")
def get_data_source_database_collections(registry_name, source_name, database_name):
    if registry_name == data_registry_id:
        results = data_registry.get_source_database_collections(source_name, database_name)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.get("/source/{source_name}/database/{database_name}/collection/{collection_name}")
def get_data_source_database_collection(registry_name, source_name, database_name, collection_name):
    if registry_name == data_registry_id:
        result = data_registry.get_source_database_collection(source_name, database_name, collection_name)
        return JSONResponse(content={"result": result})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.post("/source/{source_name}/database/{database_name}/collection/{collection_name}")
def add_data_source_database_collection(registry_name, source_name, database_name, collection_name, data: Data):
    if registry_name == data_registry_id:
        # TODO: properties
        data_registry.register_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.put("/source/{source_name}/database/{database_name}/collection/{collection_name}")
def update_source_database_collection(registry_name, source_name, database_name, collection_name, data: Data, sync: bool = False, recursive: bool = False):
    if registry_name == data_registry_id:
        # TODO: properties
        data_registry.update_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
        if sync:
            data_registry.sync_source_database_collection(source_name, database_name, collection_name, recursive=recursive, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.delete("/source/{source_name}/database/{database_name}/collection/{collection_name}")
def delete_source_database_collection(registry_name, source_name, database_name, collection_name):
    if registry_name == data_registry_id:
        data_registry.deregister_source_database_collection(source_name, database_name, collection_name, rebuild=True)
        # save
        data_registry.dump("/blue_data/config/" + data_registry_id + ".data.json")
        return JSONResponse(content={"message": "Success"})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})


@router.get("/search")
def search_data(registry_name, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    if registry_name == data_registry_id:
        results = data_registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
        return JSONResponse(content={"results": results})
    else:
        return JSONResponse(content={"message": "Error: Unknown Registry"})
