import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from urllib.parse import urlencode

import click
import dotenv
import requests
import tabulate
from click import Context

from blue.commands.helper import RESERVED_KEYS, bcolors
from blue.commands.profile import ProfileManager


class SessionManager:
    def __init__(self) -> None:
        self.__initialize()

    def __initialize(self):
        pass

    def create_session(self, NAME=None, DESCRIPTION=None):
        profile = ProfileManager().get_selected_profile()
        api_server = os.environ['BLUE_PUBLIC_API_SERVER']

        r = requests.post('http://' + api_server + '/sessions/session')
        rjson = None
        if r.status_code == 200:
            rjson = r.json()
            result = rjson['result']
            print(f"{bcolors.OKBLUE}{'Session Created:'}{bcolors.ENDC}")
            table = []
            table.append([result['id'], result['name'], result['description']])
            print(
                tabulate.tabulate(
                    table,
                    headers=["id", "name", "description"],
                    tablefmt="plain",
                )
            )
        else:
            print(r.json())

    def join_session(self, session_id, REGISTRY_NAME='default', AGENT_NAME=None, AGENT_PROPERTIES="{}"): 
        profile = ProfileManager().get_selected_profile()
        api_server = os.environ['BLUE_PUBLIC_API_SERVER']

        r = requests.post('http://' + api_server + '/sessions/session/' + session_id + "/agents/" + REGISTRY_NAME + "/agent/" + AGENT_NAME, data=AGENT_PROPERTIES)
        rjson = None
        if r.status_code == 200:
            rjson = r.json()
            print(rjson)
        else:
            print(r.json())

    def get_session_list(self):
        profile = ProfileManager().get_selected_profile()
        api_server = os.environ['BLUE_PUBLIC_API_SERVER']
        
        r = requests.get('http://' + api_server + '/sessions')
        rjson = None
        results = {}
        message = None
        if r.status_code == 200:
            rjson = r.json()
            
            for result in rjson['results']:
                results[result['id']] = result
        else:
            message = r.json()

        return results, message
            

    def list_sessions(self):
        results, message = self.get_session_list()
        
        if message is None:
            results = results.values()
            table = []
            for result in results:
                table.append([result['id'], result['name'], result['description']])

            print(f"{bcolors.OKBLUE}{'Sessions:'}{bcolors.ENDC}")
            print(tabulate.tabulate(table, headers=["id", "name", "description"], tablefmt="plain"))
        else:
            print(message)


    def parse_ctx_args(self, ctx: Context) -> dict:
        options = {}
        index = 0
        while index < len(ctx.args):
            element = ctx.args[index]
            if element.startswith("--"):
                name = element[2:]
                start = index + 1
                if ctx.args[start].startswith("--"):
                    index += 1
                    continue
                end = start + 1
                while end < len(ctx.args) and not ctx.args[end].startswith("--"):
                    end += 1
                if end - start > 1:
                    options[name] = ctx.args[start:end]
                else:
                    options[name] = ctx.args[start]
            index = end
        return options

class SessionID(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super(SessionID, self).parse_args(ctx, args)

@click.group(cls=SessionID, help="command group to interact with blue sessions")
@click.argument("session-id", required=False)
@click.pass_context
def session(ctx: Context, session_id):
    global session_mgr
    session_mgr = SessionManager()
    ctx.ensure_object(dict)
    ctx.obj["session_id"] = session_id


# session commands
@session.command(help="create a new session",)
@click.option(
    "--NAME",
    required=False,
    default="default",
    help="name of the session",
)
@click.option(
    "--DESCRIPTION",
    required=False,
    default="default",
    help="description of the session",
)
def create(name, description):
    session_mgr.create_session(NAME=name, DESCRIPTION=description)

@session.command(help="list sessions")
def ls():
    session_mgr.list_sessions()

@click.option(
    "--REGISTRY_NAME",
    required=False,
    default="default",
    help="name of the agent registry",
)
@click.option(
    "--AGENT_NAME",
    required=True,
    default="default",
    help="name of the agent",
)
@click.option(
    "--AGENT_PROPERTIES",
    required=False,
    default="{}",
    help="properties of the agent in JSON",
)
@session.command(help="add an agent to a session",)
def join(registry_name, agent_name, agent_properties):
    ctx = click.get_current_context()
    session_id = ctx.obj["session_id"]
    if len(session_id) == 0:
        raise Exception(f"missing session_id")
    sessions, message = session_mgr.get_session_list()

    if message is None:
        if session_id not in sessions:
            raise Exception(f"session {session_id} does not exist")
        
        session_mgr.join_session(session_id, REGISTRY_NAME=registry_name, AGENT_NAME=agent_name, AGENT_PROPERTIES=agent_properties)
    else:
        print(message)
   
    
