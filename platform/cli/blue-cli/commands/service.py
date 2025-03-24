import string

import click
import pydash
from click import Context

from blue_cli.helper import RESERVED_KEYS, bcolors, show_output
from blue_cli.manager import Authentication, ServiceManager
        
@click.group(help="command group to interact with blue services")
@click.option("--service_name", default=None, required=False, help="name of the service, default is selected service")
@click.option("--output", default='table', required=False, type=str, help="output format (table|json|csv)")
@click.option("--query", default="$", required=False, type=str, help="query on output results")
@click.pass_context
@click.version_option()
def service(ctx: Context, service_name, output, query):
    global service_mgr
    service_mgr = ServiceManager()
    ctx.ensure_object(dict)
    ctx.obj["service_name"] = service_name
    ctx.obj["output"] = output
    ctx.obj["query"] = query


# service commands
@service.command(help="list all services")
def ls():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    services = service_mgr.get_service_list()
    selected_service = service_mgr.get_selected_service_name()
    data = []
    for service in services:
        if output == "table":
            prefix = "*" if selected_service == service else " "
            cells = [f"{prefix} {service}"]
            if output == "table":
                if selected_service == service:
                    cells = [f"{bcolors.OKGREEN}{prefix} {service}{bcolors.ENDC}"]
            data.append(cells)
        else:
            data.append({"name": service, "selected": (selected_service == service)})

    show_output(data, ctx, single=True, headers=["name", "selected"], tablefmt="plain")

@click.pass_context
@service.command(help="show service values")
def show():
    ctx = click.get_current_context()
    output = ctx.obj["output"]
    service_name = ctx.obj["service_name"]
    if service_name is None:
        service_name = service_mgr.get_selected_service_name()
    if service_name not in service_mgr.get_service_list():
        raise Exception(f"service {service_name} does not exist")
    service = dict(service_mgr.get_service(service_name=service_name))
    if output == "table":
        data = []
    else:
        data = {}
    for key in service:
        value = service[key]
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
        print(f"{bcolors.OKBLUE}{service_name}{bcolors.ENDC}")

    show_output(data, ctx, tablefmt="plain")

@click.pass_context
@service.command(short_help="create a blue service")
def create():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if service_name is None:
        service_name = 'default'

    if service_name in service_mgr.get_service_list():
        raise Exception(f"service {service_name} exists")
    
    # create service
    service_mgr.create_service(service_name)

    # inquire service attributes from user, update
    service_mgr.inquire_service_attributes(service_name=service_name)

@click.pass_context
@service.command(short_help="install a blue service")
def install():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if service_name is None:
        service_name = 'default'

    if service_name not in service_mgr.get_service_list():
        raise Exception(f"service {service_name} does not exists")
    
    # install service
    service_mgr.install_service(service_name)

@click.pass_context
@service.command(short_help="uninstall a blue service")
def uninstall():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if service_name is None:
        service_name = 'default'

    if service_name not in service_mgr.get_service_list():
        raise Exception(f"service {service_name} does not exists")
    
    # uninstall service
    service_mgr.uninstall_service(service_name)


@click.pass_context
@service.command(short_help="starts a blue service")
def start():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if service_name is None:
        service_name = 'default'

    if service_name not in service_mgr.get_service_list():
        raise Exception(f"service {service_name} does not exists")
    
    # start service
    service_mgr.start_service(service_name)

@click.pass_context
@service.command(short_help="stop a blue service")
def stop():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    output = ctx.obj["output"]
    allowed_characters = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_")
    if service_name is None:
        service_name = 'default'

    if service_name not in service_mgr.get_service_list():
        raise Exception(f"service {service_name} does not exists")
    
    # stop service
    service_mgr.stop_service(service_name)

@click.pass_context
@service.command(short_help="select a blue service")
def select():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    if service_name is None:
        raise Exception(f"service name cannot be empty")

    service_mgr.select_service(service_name)

@click.pass_context
@service.command(
    short_help="remove a blue service",
    help="service_name: name of blue service to remove, use blue service ls to see a list of services",
)
def delete():
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    if service_name is None:
        raise Exception(f"service name cannot be empty")
    service_mgr.delete_service(service_name)


@click.pass_context
@click.argument("value", required=False)
@click.argument("key", required=False)
@service.command(
    short_help="update service configurations and variables",
    help="key value: add or update key value pair",
)
def config(key: str, value):
    if key is not None and key.lower() in RESERVED_KEYS:
        key = key.upper()
    ctx = click.get_current_context()
    service_name = ctx.obj["service_name"]
    if service_name is None:
        service_name = service_mgr.get_selected_service_name()
    if key is not None:
        
        # save to service attrs
        service_mgr.set_service_attribute(
            service_name=service_name,
            attribute_name=key,
            attribute_value=value,
        )
    else:
        service_mgr.inquire_service_attributes(service_name=service_name)


if __name__ == "__main__":
    service()

