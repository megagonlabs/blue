import click

from .commands.profile import profile
from .commands.session import session
from .commands.authentication import Authentication
import nest_asyncio

nest_asyncio.apply()


@click.group()
def cli():
    pass


@cli.command("login")
def login():
    auth = Authentication()
    cookie = auth.get_cookie()
    print(cookie)


cli.add_command(profile)
cli.add_command(session)
