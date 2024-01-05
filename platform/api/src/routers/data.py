
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


@router.get("/{registry_name}/search")
def search_agents(registry_name, keywords, approximate: bool = False, hybrid: bool = False, type: str = None, scope: str = None, page: int = 0, page_size: int = 10):
    registry = DataRegistry(registry_name)
    results = registry.search_records(keywords, type=type, scope=scope, approximate=approximate, hybrid=hybrid, page=page, page_size=page_size)
    return JSONResponse(content={ "results": results })