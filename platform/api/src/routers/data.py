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


###### Blue
from data_registry import DataRegistry


###### FastAPI
import APIRouter
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import BaseModel

router = APIRouter(prefix="/data")

###### Properties
PROPERTIES = os.getenv("BLUE__PROPERTIES")
PROPERTIES = json.loads(PROPERTIES)


###### Schema
class Data(BaseModel):
    name: str
    description: Union[str, None] = None


######


@router.get("/")
def get_data():
    registry = DataRegistry("default", properties=PROPERTIES)
    results = registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{registry_name}")
def get_data_from(registry_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    results = registry.list_records()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{registry_name}/sources")
def get_data_sources(registry_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    results = registry.get_sources()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{registry_name}/source/{source_name}")
def get_data_source(registry_name, source_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_source(source_name)
    return JSONResponse(content={"result": result})


@router.post("/{registry_name}/source/{source_name}")
def add_source(registry_name, source_name, data: Data):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.register_source(
        source_name, description=data.description, properties={}, rebuild=True
    )
    return JSONResponse(content={"message": "Success"})


@router.put("/{registry_name}/source/{source_name}")
def update_source(
    registry_name, source_name, data: Data, sync: bool = False, recursive: bool = False
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.update_source(
        source_name, description=data.description, properties={}, rebuild=True
    )
    if sync:
        registry.sync_source(source_name, recursive=recursive, rebuild=True)

    return JSONResponse(content={"message": "Success"})


@router.delete("/{registry_name}/source/{source_name}")
def delete_source(registry_name, source_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    registry.deregister_source(source_name, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.get("/{registry_name}/source/{source_name}/databases")
def get_data_source_databases(registry_name, source_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    results = registry.get_source_databases(source_name)
    return JSONResponse(content={"results": results})


@router.get("/{registry_name}/source/{source_name}/database/{database_name}")
def get_data_source_database(registry_name, source_name, database_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_source_database(source_name, database_name)
    return JSONResponse(content={"result": result})


@router.post("/{registry_name}/source/{source_name}/database/{database_name}")
def add_data_source_database(registry_name, source_name, database_name, data: Data):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.register_source_database(
        source_name,
        database_name,
        description=data.description,
        properties={},
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.put("/{registry_name}/source/{source_name}/database/{database_name}")
def update_source_database(
    registry_name,
    source_name,
    database_name,
    data: Data,
    sync: bool = False,
    recursive: bool = False,
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.update_source_database(
        source_name,
        database_name,
        description=data.description,
        properties={},
        rebuild=True,
    )
    if sync:
        registry.sync_source_database(
            source_name, database_name, recursive=recursive, rebuild=True
        )
    return JSONResponse(content={"message": "Success"})


@router.delete("/{registry_name}/source/{source_name}/database/{database_name}")
def delete_source_database(registry_name, source_name, database_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    registry.deregister_source_database(source_name, database_name, rebuild=True)
    return JSONResponse(content={"message": "Success"})


@router.get(
    "/{registry_name}/source/{source_name}/database/{database_name}/collections"
)
def get_data_source_database_collections(registry_name, source_name, database_name):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    results = registry.get_source_database_collections(source_name, database_name)
    return JSONResponse(content={"results": results})


@router.get(
    "/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}"
)
def get_data_source_database_collection(
    registry_name, source_name, database_name, collection_name
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    result = registry.get_source_database_collection(
        source_name, database_name, collection_name
    )
    return JSONResponse(content={"result": result})


@router.post(
    "/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}"
)
def add_data_source_database_collection(
    registry_name, source_name, database_name, collection_name, data: Data
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.register_source_database_collection(
        source_name,
        database_name,
        collection_name,
        description=data.description,
        properties={},
        rebuild=True,
    )
    return JSONResponse(content={"message": "Success"})


@router.put(
    "/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}"
)
def update_source_database_collection(
    registry_name,
    source_name,
    database_name,
    collection_name,
    data: Data,
    sync: bool = False,
    recursive: bool = False,
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    # TODO: properties
    registry.update_source_database_collection(
        source_name,
        database_name,
        collection_name,
        description=data.description,
        properties={},
        rebuild=True,
    )
    if sync:
        registry.sync_source_database_collection(
            source_name,
            database_name,
            collection_name,
            recursive=recursive,
            rebuild=True,
        )
    return JSONResponse(content={"message": "Success"})


@router.delete(
    "/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}"
)
def delete_source_database_collection(
    registry_name, source_name, database_name, collection_name
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    registry.deregister_source_database_collection(
        source_name, database_name, collection_name, rebuild=True
    )
    return JSONResponse(content={"message": "Success"})


@router.get("/{registry_name}/search")
def search_data(
    registry_name,
    keywords,
    approximate: bool = False,
    hybrid: bool = False,
    type: str = None,
    scope: str = None,
    page: int = 0,
    page_size: int = 10,
):
    registry = DataRegistry(registry_name, properties=PROPERTIES)
    results = registry.search_records(
        keywords,
        type=type,
        scope=scope,
        approximate=approximate,
        hybrid=hybrid,
        page=page,
        page_size=page_size,
    )
    return JSONResponse(content={"results": results})


# OBSOLETE
#
# @router.get("/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}/profile/{profile_id}")
# def get_skill_duration_given_profile(registry_name, source_name, database_name, collection_name, profile_id):
#     registry = DataRegistry(registry_name, properties=PROPERTIES)
#     source_connection = registry.connect_source(source_name)
#     db_client = source_connection.connection
#     db = db_client[database_name][collection_name]
#     db_cursor = db.find(
#             {'profileId':profile_id},
#             {'extractions.skill.duration':1})
#     skills_duration_dict_ls = []
#     for dbc in db_cursor:
#         skills_duration_dict_ls.append(dbc)
#     skills_duration_dict = skills_duration_dict_ls[0]['extractions']['skill']['duration']
#     skills_duration_tuple = sorted(
#         skills_duration_dict.items(),
#         key=lambda x:x[1],
#         reverse=True)
#     result = {}
#     for i, t in enumerate(skills_duration_tuple):
#         if i>2:
#             break
#         skill, duration = t
#         result[skill] = duration
#     return JSONResponse(content={ "result": result })

# @router.get("/{registry_name}/source/{source_name}/database/{database_name}/collection/{collection_name}/next_title/{next_title}")
# def get_insights_jt_req_skill(registry_name, source_name, database_name, collection_name, next_title):
#     registry = DataRegistry(registry_name, properties=PROPERTIES)
#     source_connection = registry.connect_source(source_name)
#     db_client = source_connection.connection
#     #next_title = "hse officer"
#     title_query = '''
#         MATCH (j:JobTitle{{name: '{}'}})-[r:requires]->(s:Skill)
#         RETURN s.name as skill, r.duration as duration
#         ORDER BY r.duration DESC
#         LIMIT 3
#     '''.format(next_title)
#     result = db_client.run_query(title_query)
#     return JSONResponse(content={ "result": result })
