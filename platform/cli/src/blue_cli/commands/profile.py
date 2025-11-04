import os
import string
import asyncio
import subprocess
import sys
import time
import json

import webbrowser
import websockets
from websockets import exceptions as ws_exceptions

import configparser
import click
import pydash
from click import Context

from blue_cli.helper import RESERVED_KEYS, bcolors, show_output
from blue_cli.manager import Authentication, ProfileManager, PlatformManager


@click.group(help="command group to interact with blue profiles")
@click.option("--profile_name", default=None, required=False, help="name of the profile, default is selected profile")
@click.option("--output", default='table', required=False, type=str, help="output format (table|json|csv)")
@click.option("--query", default="$", required=False, type=str, help="query on output results")
@click.pass_context
@click.version_option()
def profile(ctx: Context, profile_name, output, query):
    global profile_mgr
    profile_mgr = ProfileManager()
    ctx.ensure_object(dict)
    ctx.obj["profile_name"] = profile_name
    ctx.obj["output"] = output
    ctx.obj["query"] = query


# profile commands
@profile.command(help="list all profiles")
def ls():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    profiles = profile_mgr.get_profile_list()
    selected_profile = profile_mgr.get_selected_profile_name()
    data = []
    for profile in profiles:
        if output == "table":
            prefix = "*" if selected_profile == profile else " "
            cells = [f"{prefix} {profile}"]
            if output == "table":
                if selected_profile == profile:
                    cells = [f"{bcolors.OKGREEN}{prefix} {profile}{bcolors.ENDC}"]
            data.append(cells)
        else:
            data.append({"name": profile, "selected": (selected_profile == profile)})

    show_output(data, ctx, single=True, headers=["name", "selected"], tablefmt="plain")


@profile.command(help="show profile values")
def show():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    profile_name = ctx.obj["profile_name"]
    if profile_name is None:
        profile_name = profile_mgr.get_selected_profile_name()
    if profile_name not in profile_mgr.get_profile_list():
        raise Exception(f"profile {profile_name} does not exist")
    profile = dict(profile_mgr.get_profile(profile_name=profile_name))
    if output == "table":
        data = []
    else:
        data = {}
    for key in profile:
        value = profile[key]
        if pydash.is_equal(key, "BLUE_COOKIE"):
            if not pydash.is_empty(value):
                value = f'{bcolors.OKGREEN}\u2714{bcolors.ENDC}'
            else:
                value = f'{bcolors.FAIL}\u274C{bcolors.ENDC}'
        if output == "table":
            data.append([key, value])
        else:
            data[key] = value

    if output == "table":
        print(f"{bcolors.OKBLUE}{profile_name}{bcolors.ENDC}")

    show_output(data, ctx, tablefmt="plain")


@profile.command(short_help="create a blue profile")
def create():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if profile_name is None:
        profile_name = 'default'

    if profile_name in profile_mgr.get_profile_list():
        raise Exception(f"profile {profile_name} exists")

    # create profile
    profile_mgr.create_profile(profile_name)

    # inquire profile attributes from user, update
    profile_mgr.inquire_profile_attributes(profile_name=profile_name)


@profile.command(short_help="select a blue profile")
def select():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if profile_name is None:
        raise Exception(f"profile name cannot be empty")

    profile_mgr.select_profile(profile_name)


@profile.command(
    short_help="remove a blue profile",
    help="profile_name: name of blue profile to remove, use blue profile ls to see a list of profiles",
)
def delete():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if profile_name is None:
        raise Exception(f"profile name cannot be empty")
    profile_mgr.delete_profile(profile_name)


@profile.command("authenticate")
def authenticate():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if profile_name is None:
        profile_name = profile_mgr.get_selected_profile_name()

        if profile_name is None:
            raise Exception(f"profile name cannot be empty")

    profile_mgr.authenticate_profile(profile_name=profile_name)
    


@click.pass_context
@click.argument("value", required=False)
@click.argument("key", required=False)
@profile.command(
    short_help="update profile configurations and variables",
    help="key value: add or update key value pair",
)
def config(key: str, value):
    if key is not None and key.lower() in RESERVED_KEYS:
        key = key.upper()
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if profile_name is None:
        profile_name = profile_mgr.get_selected_profile_name()
    if key is not None:
        if key == "BLUE_UID" or key == "BLUE_COOKIE":
            authenticate()
            return
        else:
            # set in profile
            profile_mgr.set_profile_attribute(
                profile_name=profile_name,
                attribute_name=key,
                attribute_value=value,
            )
    else:
        profile_mgr.inquire_profile_attributes(profile_name=profile_name)


if __name__ == "__main__":
    profile()
