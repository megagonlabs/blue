###### OS / Systems
from curses import noecho
import sys

from fastapi import Depends, Request
import pydash
from constant import PermissionDenied, account_id_header, acl_enforce

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent_registry/")
sys.path.append("./lib/platform/")


###### Parsers, Formats, Utils
import json
import logging
from utils import json_utils

###### Docker
import docker

##### Typing
from typing import Union, Any, Dict, List

###### FastAPI, Web, Auth
from APIRouter import APIRouter
from fastapi.responses import JSONResponse


###### Schema
JSONObject = Dict[str, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject, Any]
######


###### Blue
from blueprint import Platform
from agent_registry import AgentRegistry


###### Properties
from settings import ACL, PROPERTIES

### Assign from platform properties
platform_id = PROPERTIES["platform.name"]
prefix = 'PLATFORM:' + platform_id
agent_registry_id = PROPERTIES["agent_registry.name"]
PLATFORM_PREFIX = f'/blue/platform/{platform_id}'


###### Initialization
p = Platform(id=platform_id, properties=PROPERTIES)
agent_registry = AgentRegistry(id=agent_registry_id, prefix=prefix, properties=PROPERTIES)


##### ROUTER
router = APIRouter(prefix=f"{PLATFORM_PREFIX}/platform", dependencies=[Depends(account_id_header)])

# set logging
logging.getLogger().setLevel("INFO")


@router.get('/settings')
def get_platform_settings(request: Request):
    return JSONResponse(content={"settings": p.get_metadata('settings')})


@router.put('/settings/{name}')
async def set_platform_setting(request: Request, name):
    payload = await request.json()
    p.set_metadata(f'settings.{name}', payload.get('value'))
    return JSONResponse(content={"message": "Success"})
