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
import copy

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
from blue.platform import Platform
from blue.agents.registry import AgentRegistry
from blue.utils.string_utils import encode_websafe_no_padding

###### Properties
from settings import EMAIL_DOMAIN_WHITE_LIST, PROPERTIES

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
    acl_enforce(request.state.user['role'], 'platform_settings', ['read_all'])
    return JSONResponse(content={"settings": {**p.get_metadata('settings'), 'allowed_domains': EMAIL_DOMAIN_WHITE_LIST.split(",")}})


@router.put('/settings/{name}')
async def set_platform_setting(request: Request, name):
    acl_enforce(request.state.user['role'], 'platform_settings', ['write_all'])
    payload = await request.json()
    p.set_metadata(f'settings.{name}', payload.get('value'))
    return JSONResponse(content={"message": "Success"})


@router.put('/settings/allowed_emails/{email}')
def add_to_email_whitelist(request: Request, email):
    acl_enforce(request.state.user['role'], 'platform_settings', ['write_all'])
    urlsafe_encoded_string = encode_websafe_no_padding(email)
    p.set_metadata(f'settings.allowed_emails.{urlsafe_encoded_string}', {'email': email, 'allow': True})
    return JSONResponse(content={"message": "Success"})


@router.delete('/settings/allowed_emails/{email}')
def remove_from_email_whitelist(request: Request, email):
    acl_enforce(request.state.user['role'], 'platform_settings', ['write_all'])
    urlsafe_encoded_string = encode_websafe_no_padding(email)
    p.set_metadata(f'settings.allowed_emails.{urlsafe_encoded_string}.allow', False)
    return JSONResponse(content={"message": "Success"})
