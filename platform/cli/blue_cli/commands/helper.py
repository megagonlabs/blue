import os
import subprocess
import json
from base64 import b64encode

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

    if default:
        user_input = input(f"{prompt} [default: {default}]: ")
    else:
        user_input = input(f"{prompt}: ")
   
    
    if user_input:
        user_input = convert(user_input, cast=cast)
        if type(user_input) == Exception:
            print(str(user_input))
            return inquire_user_input(prompt, default=default, required=required, cast=cast)
        return user_input
    else:
        if default:
            return default
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
            if value.upper() == "FALSE":
                value = False 
            elif value.upper() == "TRUE":
                value = True 
            else:
                value = Exception("value must be: bool")
        elif cast == 'str':
            value = str(value)
   
    return value