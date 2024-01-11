###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
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
from session import Session
from platform import Platform

###### FastAPI
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import BaseModel

router = APIRouter(prefix="/platform")


@router.get("/")
def get_sessions():
    platform = Platform("default")
    results = platform.get_sessions()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{platform_name}")
def get_sessions_from(platform_name):
    platform = Platform(platform_name)
    results = platform.get_sessions()
    return JSONResponse(content={"results": list(results.values())})


@router.get("/{platform_name}/session/{session_id}")
def get_session(platform_name, session_id):
    platform = Platform(platform_name)
    result = platform.get_session(session_id)
    return JSONResponse(content={"result": result})


@router.post("/{platform_name}/session")
def create_session(platform_name):
    platform = Platform(platform_name)
    result = platform.create_session()
    return JSONResponse(content={"result":result, "message": "Success"})

@router.delete("/{platform_name}/session/{session_id}")
def delete_session(platform_name, session_id):
    platform = Platform(platform_name)
    result = platform.delete_session()
    return JSONResponse(content={"message": "Success"})