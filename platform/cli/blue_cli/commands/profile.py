import configparser
import os
import string

import click
import pydash
import tabulate
from click import Context

from blue_cli.commands.helper import RESERVED_KEYS, bcolors
import blue_cli.commands.json_utils as json_utils

from io import StringIO
import json
import pandas as pd

tabulate.PRESERVE_WHITESPACE = True


def show_output(data, ctx, **options):
    output = ctx.obj["output"]
    query = ctx.obj["query"]

    single = True
    if 'single' in options:
        single = options['single']
        del options['single']

    results = json_utils.json_query(data, query, single=single)

    if output == "table":
        print(tabulate.tabulate(results, **options))
    elif output == "json":
        print(json.dumps(results, indent=3))
    elif output == "csv":
        if type(results) == dict:
            results = [results]

        df = pd.DataFrame(results)
        print(df.to_csv())
    else:
        print('Unknown output format: ' + output)

def inquire_user_input(prompt, default=None, required=False):
    if required:
        user_input = input(f"{prompt}: ")
    else:
        if default:
            user_input = input(f"{prompt} [default: {default}]: ")
        else:
            user_input = input(f"{prompt}: ")
   
    if required:
        if user_input == "":
            return inquire_user_input(prompt, default=default, required=required)
        else:
            return user_input
    else:
        if user_input:
            return user_input
        else:
            return default
        
class ProfileManager:
    def __init__(self):
        self.__initialize()

    def __initialize(self):
        # create .blue directory, if not existing
        if not os.path.exists(os.path.expanduser("~/.blue")):
            os.makedirs(os.path.expanduser("~/.blue"))

        # set profiles path
        self.profiles_path = os.path.expanduser("~/.blue/profiles")

        # load profile attribute config
        self.__load_profile_attributes_config()

        # read profiles
        self.__read_profiles()

        # read selected profile
        self.selected_profile = self.__get_selected_profile_name()

        # initialize default profile
        self.__initialize_default_profile()

        # activate selected profiile
        self.__activate_selected_profile()

    def __load_profile_attributes_config(self):
        self._profile_attributes_config = {}
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(f"{path}/configs/profile.json") as cfp:
            self._profile_attributes_config = json.load(cfp)
        
        print(json.dumps(self._profile_attributes_config))

    def inquire_profile_attributes(self):
        profile_attributes = {}

        for profile_attribute in self._profile_attributes_config:
            profile_attribute_config = self._profile_attributes_config[profile_attribute]
            prompt = profile_attribute_config['prompt']
            default = profile_attribute_config['default']
            required = profile_attribute_config['required']
            profile_attribute_value = inquire_user_input(prompt, default=default, required=required)

            profile_attributes[profile_attribute] = profile_attribute_value

        return profile_attributes
    
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
            self.create_profile(default_profile_name)

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

    def create_profile(
        self,
        profile_name,
        **profile_attributes
    ):
        # read profiles file
        self.__read_profiles()

        profile = profile_attributes

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

    def get_selected_profile_cookie(self):
        return {'session': self.get_selected_profile_attribute('BLUE_COOKIE')}

    def get_selected_profile_base_api_path(self):
        api_server = self.get_selected_profile_attribute('BLUE_PUBLIC_API_SERVER')
        platform_name = self.get_selected_profile_attribute('BLUE_DEPLOY_PLATFORM')
        return f'{api_server}/blue/platform/{platform_name}'


class ProfileName(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super(ProfileName, self).parse_args(ctx, args)


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
                value = u'\033[32m\u2714\033[0m'
            else:
                value = u'\033[31m\u274C\033[0m'
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

    # inquire profile attributes from user
    profile_attributes = profile_mgr.inquire_profile_attributes()

    # create profile
    profile_mgr.create_profile(profile_name, **profile_attributes)

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
    if key not in profile_mgr._profile_attributes_config:
        print("Unknown profile configuration key")
    ctx = click.get_current_context()
    profile_name = ctx.obj["profile_name"]
    if profile_name is None:
        profile_name = profile_mgr.get_selected_profile_name()
    if key is not None:
        profile_mgr.set_profile_attribute(
            profile_name=profile_name,
            attribute_name=key,
            attribute_value=value,
        )


if __name__ == "__main__":
    profile()

