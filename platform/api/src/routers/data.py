
###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/data_registry/')
sys.path.append('./lib/platform/')


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


###### Blue
from data_registry import DataRegistry


###### FastAPI
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import BaseModel

router = APIRouter(prefix="/data")


class Data(BaseModel):
    name: str
    description:  Union[str, None] = None



@router.get("/")
def get_data():
    registry = DataRegistry("default")
    results = registry.list_records()
    return JSONResponse(content={ "results": list(results.values()) })


@router.get("/{registry_name}")
def get_data_from(registry_name):
    registry = DataRegistry(registry_name)
    results = registry.list_records()
    return JSONResponse(content={ "results": list(results.values()) })

@router.get("/{registry_name}/sources")
def get_data_sources(registry_name):
    registry = DataRegistry(registry_name)
    results = registry.get_sources()
    return JSONResponse(content={ "results": list(results.values()) })

@router.get("/{registry_name}/source/{source_name}")
def get_data_source(registry_name, source_name):
    registry = DataRegistry(registry_name)
    result = registry.get_source(source_name)
    return JSONResponse(content={ "result": result })

@router.post("/{registry_name}/source/{source_name}")
def add_source(registry_name, source_name, data: Data):
    registry = DataRegistry(registry_name)
    #TODO: properties
    registry.register_source(source_name, description=data.description, properties={}, rebuild=True)
    return JSONResponse(content={ "message": "Success" })

@router.put("/{registry_name}/source/{source_name}")
def update_source(registry_name, source_name, data: Data, sync: bool = False, recursive: bool = False):
    registry = DataRegistry(registry_name)
    #TODO: properties
    registry.update_source(source_name, description=data.description, properties={}, rebuild=True)
    if sync:
        registry.sync_source(source_name, recursive=recursive, rebuild=True)

    return JSONResponse(content={ "message": "Success" }) 

@router.delete("/{registry_name}/source/{source_name}")
def delete_source(registry_name, source_name):
    registry = DataRegistry(registry_name)
    registry.deregister_source(source_name, rebuild=True)
    return JSONResponse(content={ "message": "Success" })

@router.get("/{registry_name}/source/{source_name}/databases")
def get_data_source_databases(registry_name, source_name):
    registry = DataRegistry(registry_name)
    results = registry.get_source_databases(source_name)
    return JSONResponse(content={ "results": list(results.values()) })

@router.get("/{registry_name}/source/{source_name}/database/{database_name}")
def get_data_source_database(registry_name, source_name, database_name):
    registry = DataRegistry(registry_name)
    result = registry.get_source_database(source_name, database_name)
    return JSONResponse(content={ "result": result })


@router.post("/{registry_name}/source/{source_name}/database/{database_name}")
def add_data_source_database(registry_name, source_name, database_name, data: Data):
    registry = DataRegistry(registry_name)
    #TODO: properties
    registry.register_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
    return JSONResponse(content={ "message": "Success" })

@router.put("/{registry_name}/source/{source_name}/database/{database_name}")
def update_source_database(registry_name, source_name, database_name, data: Data, sync: bool = False, recursive: bool = False):
    registry = DataRegistry(registry_name)
    #TODO: properties
    registry.update_source_database(source_name, database_name, description=data.description, properties={}, rebuild=True)
    if sync:
        registry.sync_source_database(source_name, database_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={ "message": "Success" })  

@router.delete("/{registry_name}/source/{source_name}/database/{database_name}")
def delete_source_database(registry_name, source_name, database_name):
    registry = DataRegistry(registry_name)
    registry.deregister_source_database(source_name, database_name, rebuild=True)
    return JSONResponse(content={ "message": "Success" })

@router.get("/{registry_name}/source/{source_name}/database/{database_name}/collections")
def get_data_source_database_collections(registry_name, source_name, database_name):
    registry = DataRegistry(registry_name)
    results = registry.get_source_database_collections(source_name, database_name)
    return JSONResponse(content={ "results": list(results.values()) })

@router.get("/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}")
def get_data_source_database_collection(registry_name, source_name, database_name, collection_name):
    registry = DataRegistry(registry_name)
    result = registry.get_source_database_collection(source_name, database_name, collection_name)
    return JSONResponse(content={ "result": result })

@router.post("/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}")
def add_data_source_database_collection(registry_name, source_name, database_name, collection_name, data: Data):
    registry = DataRegistry(registry_name)
    #TODO: properties
    registry.register_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
    return JSONResponse(content={ "message": "Success" })

@router.put("/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}")
def update_source_database_collection(registry_name, source_name, database_name, collection_name, data: Data, sync: bool = False, recursive: bool = False):
    registry = DataRegistry(registry_name)
    #TODO: properties
    registry.update_source_database_collection(source_name, database_name, collection_name, description=data.description, properties={}, rebuild=True)
    if sync:
        registry.sync_source_database_collection(source_name, database_name, collection_name, recursive=recursive, rebuild=True)
    return JSONResponse(content={ "message": "Success" })   

@router.delete("/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}")
def delete_source_database_collection(registry_name, source_name, database_name, collection_name):
    registry = DataRegistry(registry_name)
    registry.deregister_source_database_collection(source_name, database_name, collection_name, rebuild=True)
    return JSONResponse(content={ "message": "Success" })

@router.get("/{registry_name}/search")
def search_data(registry_name, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    registry = DataRegistry(registry_name)
    results = registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={ "results": results })