import click
from traitlets import default

from .commands.profile import  profile
# from .commands.session import session
from .commands.platform import platform
from .commands.service import service
from .commands.registry import registry

import nest_asyncio

nest_asyncio.apply()


#@click.group()
#def cli():
#    pass


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)  # context for subcommands

cli.add_command(profile)
cli.add_command(platform)
cli.add_command(service)
# cli.add_command(session)
cli.add_command(registry)
