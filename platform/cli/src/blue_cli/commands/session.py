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
import requests
import tabulate
from click import Context

from blue_cli.helper import bcolors
from blue_cli.commands.profile import ProfileManager
from blue_cli.commands.platform import PlatformManager

import blue_cli.commands.json_utils as json_utils

from io import StringIO
import json
import pandas as pd


def show_output(data, ctx, **options):
    output = ctx.obj["output"]
    query = ctx.obj["query"]

    single = True
    if 'single' in options:
        single = options['single']
        del options['single']

    results = json_utils.json_query(data, query, single=single)

    if output == "table":
        print(tabulate.tabulate(results, **options))
    elif output == "json":

        print(json.dumps(results, indent=3))
    elif output == "csv":
        if type(results) == dict:
            results = [results]

        df = pd.DataFrame(results)
        print(df.to_csv())
    else:
        print('Unknown output format: ' + output)


class SessionManager:
    def __init__(self) -> None:
        self.__initialize()

    def __initialize(self):
        pass

    def create_session(self, NAME=None, DESCRIPTION=None):
        profile = ProfileManager()
        cookies = profile.get_selected_profile_cookie()
        platform = PlatformManager()
        base_api_path = platform.get_selected_platform_base_api_path()

        r = requests.post(base_api_path + '/sessions/session', cookies=cookies)
        rjson = None
        result = {}
        message = None
        if r.status_code == 200:
            rjson = r.json()
            result = rjson['result']
        else:
            message = r.json()

        return result, message

    def join_session(self, session_id, REGISTRY='default', AGENT=None, AGENT_PROPERTIES="{}", AGENT_INPUT=None):
        profile = ProfileManager()
        cookies = profile.get_selected_profile_cookie()
        platform = PlatformManager()
        base_api_path = platform.get_selected_platform_base_api_path()
        r = requests.post(
            base_api_path + '/sessions/session/' + session_id + "/agents/" + REGISTRY + "/agent/" + AGENT + ("?input=" + AGENT_INPUT if AGENT_INPUT else ""),
            data=AGENT_PROPERTIES,
            cookies=cookies,
        )
        rjson = None
        result = {}
        message = None
        print(r)
        if r.status_code == 200:
            rjson = r.json()
            result = rjson['result']
        else:
            message = r.json()

        return result, message

    def get_session_list(self):
        profile = ProfileManager()
        cookies = profile.get_selected_profile_cookie()
        platform = PlatformManager()
        base_api_path = platform.get_selected_platform_base_api_path()
        r = requests.get(base_api_path + '/sessions', cookies=cookies)
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


@click.group(help="command group to interact with blue sessions")
@click.option("--session-id", default=None, required=False, help="id of the session")
@click.option("--output", default='table', required=False, type=str, help="output format (table|json|csv)")
@click.option("--query", default="$", required=False, type=str, help="query on output results")
@click.pass_context
def session(ctx: Context, session_id, output, query):
    global session_mgr
    session_mgr = SessionManager()
    ctx.ensure_object(dict)
    ctx.obj["session_id"] = session_id
    ctx.obj["output"] = output
    ctx.obj["query"] = query


# session commands
@session.command(
    help="create a new session",
)
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
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    result, message = session_mgr.create_session(NAME=name, DESCRIPTION=description)

    if message is None:
        if output == "table":
            data = []
            data.append([result['id'], result['name'], result['description']])

            print(f"{bcolors.OKBLUE}{'Session Created:'}{bcolors.ENDC}")
        else:
            data = result
        show_output(data, ctx, single=True, headers=["id", "name", "description"], tablefmt="plain")
    else:
        print(message)


@session.command(help="list sessions")
def ls():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    results, message = session_mgr.get_session_list()

    if message is None:
        results = list(results.values())
        if output == "table":
            data = []
            for result in results:
                data.append([result['id'], result['name'], result['description']])

            print(f"{bcolors.OKBLUE}{'Sessions:'}{bcolors.ENDC}")
        else:
            data = results
        show_output(data, ctx, single=True, headers=["id", "name", "description"], tablefmt="plain")
    else:
        print(message)


@session.command(
    help="add an agent to a session",
)
@click.option(
    "--REGISTRY",
    required=False,
    default="default",
    help="name of the agent registry",
)
@click.option(
    "--AGENT",
    required=True,
    default="default",
    help="name of the agent",
)
@click.option(
    "--AGENT_PROPERTIES",
    required=False,
    default="{}",
    help="optional properties of the agent in JSON",
)
@click.option(
    "--AGENT_INPUT",
    required=False,
    default=None,
    help="optional input text",
)
def join(registry, agent, agent_properties, agent_input):
    ctx = click.get_current_context()
    session_id = ctx.obj["session_id"]
    if session_id is None:
        raise Exception(f"missing session_id")
    sessions, message = session_mgr.get_session_list()

    if message is None:
        if session_id not in sessions:
            raise Exception(f"session {session_id} does not exist")

        session_mgr.join_session(session_id, REGISTRY=registry, AGENT=agent, AGENT_PROPERTIES=agent_properties, AGENT_INPUT=agent_input)
    else:
        print(message)
