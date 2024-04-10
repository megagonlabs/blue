import configparser
import os
import string

import click
import tabulate
from click import Context

from blue.commands.helper import RESERVED_KEYS, bcolors

tabulate.PRESERVE_WHITESPACE = True


class ProfileManager:
    def __init__(self):
        self.__initialize()

    def __initialize(self):
        # create .blue directory, if not existing
        if not os.path.exists(os.path.expanduser("~/.blue")):
            os.makedirs(os.path.expanduser("~/.blue"))

        # set profiles path
        self.profiles_path = os.path.expanduser("~/.blue/profiles")

        # read profiles
        self.__read_profiles()

        # read selected profile
        self.selected_profile = self.__get_selected_profile_name()

        # initialize default profile
        self.__initialize_default_profile()

        # activate selected profiile
        self.__activate_selected_profile()

    def __read_profiles(self):
        # read profiles file
        self.profiles = configparser.ConfigParser()
        self.profiles.optionxform = str
        self.profiles.read(self.profiles_path)

    def __write_profiles(self):
        # write profiles file
        with open(self.profiles_path, "w") as profilesfile:
            self.profiles.write(profilesfile, space_around_delimiters=False)

    def __get_selected_profile_name(self):
        selected_profile_path = os.path.expanduser("~/.blue/.selected_profile")
        selected_profile = "default"
        try:
            with open(selected_profile_path, "r") as profilefile:
                selected_profile = profilefile.read()
        except Exception:
            pass
        return selected_profile.strip()

    def __set_selected_profile_name(self, selected_profile_name):
        selected_profile_path = os.path.expanduser("~/.blue/.selected_profile")
        with open(selected_profile_path, "w") as profilefile:
            profilefile.write(selected_profile_name)

        self.selected_profile = selected_profile_name

    def __initialize_default_profile(self):
        default_profile_name = self.get_default_profile_name()
        if not self.has_profile(default_profile_name):
            self.create_profile(default_profile_name, AWS_PROFILE="default")

    def __activate_selected_profile(self):
        for key in self.profiles[self.selected_profile]:
            value = self.profiles[self.selected_profile][key]
            os.environ[key] = value
        

    def get_default_profile(self):
        default_profile_name = self.get_default_profile_name()
        return self.get_profile(default_profile_name)

    def get_default_profile_name(self):
        return "default"

    def get_selected_profile_name(self):
        return self.__get_selected_profile_name()

    def set_selected_profile_name(self, selected_profile_name):
        self.__set_selected_profile_name(selected_profile_name)

    def get_selected_profile(self):
        select_profile_name = self.get_selected_profile_name()
        return self.get_profile(select_profile_name)

    def update_selected_profile(self, **profile_attributes):
        # get selected profile name
        select_profile_name = self.get_selected_profile_name()
        self.update_selected_profile(select_profile_name, **profile_attributes)

        # activate selected profiile
        self.__activate_selected_profile()

    def get_selected_profile_attribute(self, attribute_name):
        # get selected profile name
        select_profile_name = self.get_selected_profile_name()
        return self.get_profile_attribute(select_profile_name, attribute_name)

    def set_selected_profile_attribute(self, attribute_name, attribute_value):
        # get selected profile name
        select_profile_name = self.get_selected_profile_name()
        self.set_profile_attribute(select_profile_name, attribute_name, attribute_value)

    def get_profile_list(self):
        # read profiles
        self.__read_profiles()

        # list sections (i.e. profile names)
        profiles = []
        for section in self.profiles.sections():
            profiles.append(section)
        return profiles

    def has_profile(self, profile_name):
        # read profiles file
        self.__read_profiles()

        # check profile
        return profile_name in self.profiles

    def get_profile(self, profile_name):
        if self.has_profile(profile_name):
            return self.profiles[profile_name]
        else:
            return None

    def create_profile(self, profile_name, AWS_PROFILE='default', BLUE_INSTALL_DIR="~/blue",BLUE_DEPLOY_TARGET="localhost",BLUE_DEPLOY_PLATFORM="default",BLUE_PUBLIC_API_SERVER="localhost:5050",BLUE_DATA_DIR="~/.blue/data"):
        # read profiles file
        self.__read_profiles()

        profile = {
            "AWS_PROFILE": AWS_PROFILE,
            "BLUE_INSTALL_DIR": BLUE_INSTALL_DIR,
            "BLUE_DEPLOY_TARGET": BLUE_DEPLOY_TARGET,
            "BLUE_DEPLOY_PLATFORM": BLUE_DEPLOY_PLATFORM,
            "BLUE_PUBLIC_API_SERVER": BLUE_PUBLIC_API_SERVER,
            "BLUE_DATA_DIR": BLUE_DATA_DIR,
        }

        # update profiles
        self.profiles[profile_name] = profile

        # write profiles file
        self.__write_profiles()

    def update_profile(self, profile_name, **profile_attributes):
        # get profile
        profile = self.get_profile(profile_name)
        profile = profile if profile else {}

        # update profile
        profile = dict(profile) | profile_attributes
        profile = {k: v for k, v in profile.items() if v is not None}
        # update profiles
        self.profiles[profile_name] = profile
        # write profiles file
        self.__write_profiles()

        # activate selected profiile
        self.__activate_selected_profile()

    def delete_profile(self, profile_name):
        # read profiles
        self.__read_profiles()

        # delete section under profile_name
        if not self.has_profile(profile_name):
            raise Exception(f"no profile named {profile_name}")
        else:
            self.profiles.pop(profile_name)
            self.__write_profiles()

    def select_profile(self, profile_name):
        self.set_selected_profile_name(profile_name)

        # activate selected profiile
        self.__activate_selected_profile()

    def get_profile_attribute(self, profile_name, attribute_name):
        # get profile
        profile = self.get_profile(profile_name)
        if profile is None:
            return None
        if attribute_name in profile:
            return profile[attribute_name]
        else:
            return None

    def set_profile_attribute(self, profile_name, attribute_name, attribute_value):
        self.update_profile(profile_name, **{attribute_name: attribute_value})


class ProfileName(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super(ProfileName, self).parse_args(ctx, args)


@click.group(cls=ProfileName, help="command group to interact with blue profiles")
@click.argument("profile-name", required=False)
@click.pass_context
@click.version_option()
def profile(ctx: Context, profile_name):
    global profile_mgr
    profile_mgr = ProfileManager()
    ctx.ensure_object(dict)
    ctx.obj["profile_name"] = profile_name


# profile commands
@profile.command(help="list all profiles")
def ls():
    profiles = profile_mgr.get_profile_list()
    selected_profile = profile_mgr.get_selected_profile_name()
    blue_profiles = []
    for profile in profiles:
        prefix = "*" if selected_profile == profile else " "
        cells = [f"{prefix} {profile}"]
        if selected_profile == profile:
            cells = [f"{bcolors.OKGREEN}{prefix} {profile}{bcolors.ENDC}"]
        blue_profiles.append(cells)
    print(
        tabulate.tabulate(
            blue_profiles,
            tablefmt="plain",
        )
    )


@profile.command(help="show profile values")
def show():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if len(profile_name) == 0:
        profile_name = profile_mgr.get_selected_profile_name()
    if profile_name not in profile_mgr.get_profile_list():
        raise Exception(f"profile {profile_name} does not exist")
    profile = dict(profile_mgr.get_profile(profile_name=profile_name))
    table = []
    for key in profile:
        table.append([key, profile[key]])
    table.sort(key=lambda x: x[0])
    print(f"{bcolors.OKBLUE}{profile_name}{bcolors.ENDC}")
    print(tabulate.tabulate(table, tablefmt="plain"))


@profile.command(short_help="create a blue profile")
@click.option(
    "--AWS_PROFILE",
    required=False,
    default="default",
    help="profile name for AWS, reference ~/.aws/credentials",
)
@click.option(
    "--BLUE_INSTALL_DIR",
    required=False,
    default="`~/blue",
    help="blue installation directory, `~/blue` (default)",
)
@click.option(
    "--BLUE_DEPLOY_TARGET",
    required=False,
    default="localhost",
    help="blue deployment target, `localhost` (default), `swarm` ",
)
@click.option(
    "--BLUE_DEPLOY_PLATFORM",
    required=False,
    default="default",
    help="blue platform name, `default` (default)",
)
@click.option(
    "--BLUE_PUBLIC_API_SERVER",
    required=False,
    default="localhost:5050",
    help="blue api server address, `http://localhost:5050` (default)",
)
@click.option(
    "--BLUE_DATA_DIR",
    required=False,
    default="~/.blue/data",
    help="directory to host blue data, `~/.blue/data` (default)",
)
def create(aws_profile, blue_install_dir, blue_deploy_target, blue_deploy_platform, blue_public_api_serveer, blue_data_dir):
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    allowed_characters = set(
        string.ascii_lowercase + string.ascii_uppercase + string.digits + "_"
    )
    valid = set(profile_name) <= allowed_characters
    if len(profile_name) == 0:
        raise Exception(f"profile name cannot be empty")
    if not valid:
        raise Exception(
            "profile name contains invalid characters; only from a-z, A-Z, 0-9, and underscore are allowed."
        )
    if profile_name in profile_mgr.get_profile_list():
        raise Exception(f"profile {profile_name} exists")
    profile_mgr.create_profile(profile_name, AWS_PROFILE=aws_profile, BLUE_INSTALL_DIR=blue_install_dir,BLUE_DEPLOY_TARGET=blue_deploy_target,BLUE_DEPLOY_PLATFORM=blue_deploy_platform,BLUE_PUBLIC_API_SERVER=blue_public_api_serveer,BLUE_DATA_DIR=blue_data_dir)


@profile.command(short_help="select a blue profile")
def select():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if len(profile_name) == 0:
        raise Exception(f"profile name cannot be empty")
    profile_mgr.select_profile(profile_name)


@profile.command(
    short_help="remove a blue profile",
    help="profile-name: name of blue profile to remove, use blue profile ls to see a list of profiles",
)
def delete():
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if len(profile_name) == 0:
        raise Exception(f"profile name cannot be empty")
    profile_mgr.delete_profile(profile_name)


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
    if len(profile_name) == 0:
        profile_name = profile_mgr.get_selected_profile_name()
    if key is not None:
        profile_mgr.set_profile_attribute(
            profile_name=profile_name,
            attribute_name=key,
            attribute_value=value,
        )
        

if __name__ == "__main__":
    profile()
