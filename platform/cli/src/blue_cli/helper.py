import os
import subprocess
import json
from base64 import b64encode
import curses

import tabulate
import pandas as pd
from blue.utils import json_utils

RESERVED_KEYS = [
    "user",
    "username",
    "password",
    "aws_profile",
    "host",
    "alp",
    "port",
    "ssh_profile",
]


def print_list_curses(stdscr, string_list):
    """Prints a list of strings to the curses window."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    for i, text in enumerate(string_list):
        try:
            stdscr.addstr(i, 0, text['message'][:width])
        except curses.error:
            pass
    stdscr.refresh()


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


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


def inquire_user_input(prompt, default=None, required=False, cast=None):

    if default is not None:
        user_input = input(f"{prompt} [default: {default}]: ")
    else:
        user_input = input(f"{prompt}: ")

    if user_input != "":
        user_input = convert(user_input, cast=cast)
        if type(user_input) == Exception:
            print(str(user_input))
            return inquire_user_input(prompt, default=default, required=required, cast=cast)
        return user_input
    else:
        if default is not None:
            return convert(default, cast=cast)
        else:
            if required:
                print("Required attribute, please enter a valid value.")
                return inquire_user_input(prompt, default=default, required=required, cast=cast)
            else:
                return None


def convert(value, cast=None):
    if cast:
        if cast == 'int':
            try:
                value = int(value)
            except Exception as e:
                value = Exception("value mist be: int")

        elif cast == 'bool':
            if type(value) == bool:
                return value
            elif type(value) == str:
                if value.upper() == "FALSE":
                    value = False
                elif value.upper() == "TRUE":
                    value = True
                else:
                    value = Exception("value must be: bool")
            else:
                value = Exception("value must be: bool")
        elif cast == 'str':
            value = str(value)
        elif cast == 'file':
            value = os.path.expanduser(value)

    return value
