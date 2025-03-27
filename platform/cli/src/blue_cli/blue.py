import click
from traitlets import default

from .commands.profile import  profile
# from .commands.session import session
from .commands.platform import platform
from .commands.service import service
import nest_asyncio

nest_asyncio.apply()


@click.group()
def cli():
    pass

cli.add_command(profile)
cli.add_command(platform)
cli.add_command(service)
# cli.add_command(session)
