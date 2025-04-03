import string

import click
import pydash
from click import Context

from blue_cli.helper import RESERVED_KEYS, bcolors, show_output
from blue_cli.manager import Authentication, PlatformManager
        
@click.group(help="command group to interact with blue platforms")
@click.option("--platform_name", default=None, required=False, help="name of the platform, default is selected platform")
@click.option("--output", default='table', required=False, type=str, help="output format (table|json|csv)")
@click.option("--query", default="$", required=False, type=str, help="query on output results")
@click.pass_context
@click.version_option()
def platform(ctx: Context, platform_name, output, query):
    global platform_mgr
    platform_mgr = PlatformManager()
    ctx.ensure_object(dict)
    ctx.obj["platform_name"] = platform_name
    ctx.obj["output"] = output
    ctx.obj["query"] = query


# platform commands
@platform.command(help="list all platforms")
def ls():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    platforms = platform_mgr.get_platform_list()
    selected_platform = platform_mgr.get_selected_platform_name()
    data = []
    for platform in platforms:
        if output == "table":
            prefix = "*" if selected_platform == platform else " "
            cells = [f"{prefix} {platform}"]
            if output == "table":
                if selected_platform == platform:
                    cells = [f"{bcolors.OKGREEN}{prefix} {platform}{bcolors.ENDC}"]
            data.append(cells)
        else:
            data.append({"name": platform, "selected": (selected_platform == platform)})

    show_output(data, ctx, single=True, headers=["name", "selected"], tablefmt="plain")


@platform.command(help="show platform values")
def show():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    platform_name = ctx.obj["platform_name"]
    if platform_name is None:
        platform_name = platform_mgr.get_selected_platform_name()
    if platform_name not in platform_mgr.get_platform_list():
        raise Exception(f"platform {platform_name} does not exist")
    platform = dict(platform_mgr.get_platform(platform_name=platform_name))
    if output == "table":
        data = []
    else:
        data = {}
    for key in platform:
        value = platform[key]
        if pydash.is_equal(key, "BLUE_COOKIE"):
            if not pydash.is_empty(value):
                value = u'\033[32m\u2714\033[0m'
            else:
                value = u'\033[31m\u274C\033[0m'
        if output == "table":
            data.append([key, value])
        else:
            data[key] = value

    if output == "table":
        print(f"{bcolors.OKBLUE}{platform_name}{bcolors.ENDC}")

    show_output(data, ctx, tablefmt="plain")


@platform.command(short_help="create a blue platform")
def create():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if platform_name is None:
        platform_name = 'default'

    if platform_name in platform_mgr.get_platform_list():
        raise Exception(f"platform {platform_name} exists")
    
    # create platform
    platform_mgr.create_platform(platform_name)

    # inquire platform attributes from user, update
    platform_mgr.inquire_platform_attributes(platform_name=platform_name)


@platform.command(short_help="install a blue platform")
def install():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if platform_name is None:
        platform_name = 'default'

    if platform_name not in platform_mgr.get_platform_list():
        raise Exception(f"platform {platform_name} does not exists")
    
    # install platform
    platform_mgr.install_platform(platform_name)

@platform.command(short_help="uninstall a blue platform")
def uninstall():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if platform_name is None:
        platform_name = 'default'

    if platform_name not in platform_mgr.get_platform_list():
        raise Exception(f"platform {platform_name} does not exists")
    
    # uninstall platform
    platform_mgr.uninstall_platform(platform_name)

@platform.command(short_help="starts a blue platform")
def start():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if platform_name is None:
        platform_name = 'default'

    if platform_name not in platform_mgr.get_platform_list():
        raise Exception(f"platform {platform_name} does not exists")
    
    # start platform
    platform_mgr.start_platform(platform_name)

@platform.command(short_help="stop a blue platform")
def stop():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if platform_name is None:
        platform_name = 'default'

    if platform_name not in platform_mgr.get_platform_list():
        raise Exception(f"platform {platform_name} does not exists")
    
    # stop platform
    platform_mgr.stop_platform(platform_name)

@platform.command(short_help="select a blue platform")
def select():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    if platform_name is None:
        raise Exception(f"platform name cannot be empty")

    platform_mgr.select_platform(platform_name)


@platform.command(
    short_help="remove a blue platform",
    help="platform_name: name of blue platform to remove, use blue platform ls to see a list of platforms",
)
def delete():
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    if platform_name is None:
        raise Exception(f"platform name cannot be empty")
    platform_mgr.delete_platform(platform_name)


@click.pass_context
@click.argument("value", required=False)
@click.argument("key", required=False)
@platform.command(
    short_help="update platform configurations and variables",
    help="key value: add or update key value pair",
)
def config(key: str, value):
    if key is not None and key.lower() in RESERVED_KEYS:
        key = key.upper()
    ctx = click.get_current_context()
    platform_name = ctx.obj["platform_name"]
    if platform_name is None:
        platform_name = platform_mgr.get_selected_platform_name()
    if key is not None:
        if key == "BLUE_USER_ROLE":
            # authenticate first
            auth = Authentication()
            cookie = auth.get_cookie()
            uid = auth.get_uid()

            platform_mgr.set_user_role(
                platform_name=platform_name,
                cookie=cookie,
                uid=uid,
                role=value
            )
            
        # save to platform attrs
        platform_mgr.set_platform_attribute(
            platform_name=platform_name,
            attribute_name=key,
            attribute_value=value,
        )
    else:
        platform_mgr.inquire_platform_attributes(platform_name=platform_name)


if __name__ == "__main__":
    platform()

