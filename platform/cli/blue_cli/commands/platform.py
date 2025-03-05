import os
import string
import json

import configparser
import click
import pydash
from click import Context

import docker

from blue_cli.commands.helper import RESERVED_KEYS, bcolors, show_output, inquire_user_input
from blue_cli.commands.profile import ProfileManager
        
class PlatformManager:
    def __init__(self):
        self.__initialize()

    def __initialize(self):
        # create .blue directory, if not existing
        if not os.path.exists(os.path.expanduser("~/.blue")):
            os.makedirs(os.path.expanduser("~/.blue"))

        # set platforms path
        self.platforms_path = os.path.expanduser("~/.blue/platforms")

        # load platform attribute config
        self.__load_platform_attributes_config()

        # read platforms
        self.__read_platforms()

        # read selected platform
        self.selected_platform = self.__get_selected_platform_name()

        # initialize default platform
        self.__initialize_default_platform()

        # activate selected profiile
        self.__activate_selected_platform()

    def __load_platform_attributes_config(self):
        self._platform_attributes_config = {}
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(f"{path}/configs/platform.json") as cfp:
            self._platform_attributes_config = json.load(cfp)

    def inquire_platform_attributes(self, platform_name=None):
        if platform_name is None:
            platform_name = self.get_default_platform_name()

        platform  = self.get_platform(platform_name)
        platform_attributes = dict(platform)

        if platform_attributes is None:
            platform_attributes = {}

        for platform_attribute in self._platform_attributes_config:
            platform_attribute_config = self._platform_attributes_config[platform_attribute]
            prompt = platform_attribute_config['prompt']
            default = platform_attribute_config['default']
            cast = platform_attribute_config['cast']
            value = default
            current = None
            if platform_attribute in platform_attributes:
                current = platform_attributes[platform_attribute]
            if current:
                value = current
            required = platform_attribute_config['required']
            if required:
                platform_attribute_value = inquire_user_input(prompt, default=value, cast=cast, required=required)
            else:
                platform_attribute_value = value

            self.set_platform_attribute(platform_name, platform_attribute, platform_attribute_value)
    
    def __read_platforms(self):
        # read platforms file
        self.platforms = configparser.ConfigParser()
        self.platforms.optionxform = str
        self.platforms.read(self.platforms_path)

    def __write_platforms(self):
        # write platforms file
        with open(self.platforms_path, "w") as platformsfile:
            self.platforms.write(platformsfile, space_around_delimiters=False)

    def __get_selected_platform_name(self):
        selected_platform_path = os.path.expanduser("~/.blue/.selected_platform")
        selected_platform = "default"
        try:
            with open(selected_platform_path, "r") as platformfile:
                selected_platform = platformfile.read()
        except Exception:
            pass
        return selected_platform.strip()

    def __set_selected_platform_name(self, selected_platform_name):
        selected_platform_path = os.path.expanduser("~/.blue/.selected_platform")
        with open(selected_platform_path, "w") as platformfile:
            platformfile.write(selected_platform_name)

        self.selected_platform = selected_platform_name

    def __initialize_default_platform(self):
        default_platform_name = self.get_default_platform_name()
        if not self.has_platform(default_platform_name):
            self.create_platform(default_platform_name)

    def __activate_selected_platform(self):
        for key in self.platforms[self.selected_platform]:
            value = self.platforms[self.selected_platform][key]
            os.environ[key] = value

    def get_default_platform(self):
        default_platform_name = self.get_default_platform_name()
        return self.get_platform(default_platform_name)

    def get_default_platform_name(self):
        return "default"

    def get_selected_platform_name(self):
        return self.__get_selected_platform_name()

    def set_selected_platform_name(self, selected_platform_name):
        self.__set_selected_platform_name(selected_platform_name)

    def get_selected_platform(self):
        select_platform_name = self.get_selected_platform_name()
        return self.get_platform(select_platform_name)

    def update_selected_platform(self, **platform_attributes):
        # get selected platform name
        select_platform_name = self.get_selected_platform_name()
        self.update_selected_platform(select_platform_name, **platform_attributes)

        # activate selected profiile
        self.__activate_selected_platform()

    def get_selected_platform_attribute(self, attribute_name):
        # get selected platform name
        select_platform_name = self.get_selected_platform_name()
        return self.get_platform_attribute(select_platform_name, attribute_name)

    def set_selected_platform_attribute(self, attribute_name, attribute_value):
        # get selected platform name
        select_platform_name = self.get_selected_platform_name()
        self.set_platform_attribute(select_platform_name, attribute_name, attribute_value)

    def get_platform_list(self):
        # read platforms
        self.__read_platforms()

        # list sections (i.e. platform names)
        platforms = []
        for section in self.platforms.sections():
            platforms.append(section)
        return platforms

    def has_platform(self, platform_name):
        # read platforms file
        self.__read_platforms()

        # check platform
        return platform_name in self.platforms

    def get_platform(self, platform_name):
        if self.has_platform(platform_name):
            return self.platforms[platform_name]
        else:
            return None

    def create_platform(
        self,
        platform_name,
        **platform_attributes
    ):
        # read platforms file
        self.__read_platforms()

        platform = platform_attributes

        # deploy platform atttribute
        platform['BLUE_DEPLOY_PLATFORM'] = platform_name

        # update platforms
        self.platforms[platform_name] = platform


        # write platforms file
        self.__write_platforms()

    def update_platform(self, platform_name, **platform_attributes):
        # get platform
        platform = self.get_platform(platform_name)
        platform = platform if platform else {}

        # update platform
        platform = dict(platform) | platform_attributes
        platform = {k: v for k, v in platform.items() if v is not None}
        # update platforms
        self.platforms[platform_name] = platform
        # write platforms file
        self.__write_platforms()

        # activate selected profiile
        self.__activate_selected_platform()

    def delete_platform(self, platform_name):
        # read platforms
        self.__read_platforms()

        # delete section under platform_name
        if not self.has_platform(platform_name):
            raise Exception(f"no platform named {platform_name}")
        else:
            self.platforms.pop(platform_name)
            self.__write_platforms()

    def install_platform(
        self,
        platform_name):
        
        ### get profile
        # get profile
        profile = ProfileManager.get_selected_profile()
        profile = profile if profile else {}
        profile = dict(profile)

        ### get platform 
        # get platform
        platform = self.get_platform(platform_name)
        platform = platform if platform else {}
        platform = dict(platform)

        
        BLUE_DATA_DIR = profile["BLUE_DATA_DIR"]
        BLUE_DEPLOY_PLATFORM = platform_name

        ### connect to docker
        client = docker.from_env()

        ### create docker volume
        # docker volume create --driver local  --opt type=none --opt device=${BLUE_DATA_DIR}/${BLUE_DEPLOY_PLATFORM} --opt o=bind blue_${BLUE_DEPLOY_PLATFORM}_data
        client.volumes.create(name=f"blue_{BLUE_DEPLOY_PLATFORM}_data", driver='local', driver_opts={'type': None, 'o': 'bind', 'device': f"{BLUE_DATA_DIR}/{BLUE_DEPLOY_PLATFORM}"})

        #### pull images

        #### docker volume content

        ## registries

        ## registry models

        ## rbac



    def select_platform(self, platform_name):
        self.set_selected_platform_name(platform_name)

        # activate selected profiile
        self.__activate_selected_platform()

    def get_platform_attribute(self, platform_name, attribute_name):
        # get platform
        platform = self.get_platform(platform_name)
        if platform is None:
            return None
        if attribute_name in platform:
            return platform[attribute_name]
        else:
            return None

    def set_platform_attribute(self, platform_name, attribute_name, attribute_value):
        if attribute_name not in self._platform_attributes_config:
            print("Unknown platform attribute")
            return
        
        self.update_platform(platform_name, **{attribute_name: attribute_value})

    def get_selected_platform_cookie(self):
        return {'session': self.get_selected_platform_attribute('BLUE_COOKIE')}

    def get_selected_platform_base_api_path(self):
        api_server = self.get_selected_platform_attribute('BLUE_PUBLIC_API_SERVER')
        platform_name = self.get_selected_platform_attribute('BLUE_DEPLOY_PLATFORM')
        return f'{api_server}/blue/platform/{platform_name}'


class platformName(click.Group):
    def parse_args(self, ctx, args):
        if len(args) > 0 and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super(platformName, self).parse_args(ctx, args)


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
        platform_mgr.set_platform_attribute(
            platform_name=platform_name,
            attribute_name=key,
            attribute_value=value,
        )
    else:
        platform_mgr.inquire_platform_attributes(platform_name=platform_name)


if __name__ == "__main__":
    platform()

