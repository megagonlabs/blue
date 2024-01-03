
###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent_registry/')
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
from agent_registry import AgentRegistry

###### FastAPI
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/agents")

print("1")
registry = AgentRegistry("default")

@router.get("/")
def get_agents():
    results = registry.list_records()
    return JSONResponse(content={ "list": list(results.values()) })
