import click

from .commands.profile import profile
from .commands.session import session


@click.group()
def cli():
    pass


cli.add_command(profile)
cli.add_command(session)
