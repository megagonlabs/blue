import click
from traitlets import default

from .commands.profile import  profile
# from .commands.session import session
from .commands.platform import platform
import nest_asyncio

nest_asyncio.apply()


@click.group()
def cli():
    pass

cli.add_command(profile)
cli.add_command(platform)
# cli.add_command(session)
