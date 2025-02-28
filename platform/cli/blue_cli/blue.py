import click
from traitlets import default

from .commands.profile import ProfileManager, profile
from .commands.session import session
from .commands.authentication import Authentication
import nest_asyncio

nest_asyncio.apply()


@click.group()
def cli():
    pass


@cli.command("login")
@click.option('--uid', is_flag=True, default=False, required=False, help="show user ID")
def login(uid):
    auth = Authentication()
    cookie = auth.get_cookie()
    # save cookie under current blue user profile
    ProfileManager().set_selected_profile_attribute('BLUE_COOKIE', cookie)
    if uid:
        print(auth.get_uid())


cli.add_command(profile)
cli.add_command(session)
