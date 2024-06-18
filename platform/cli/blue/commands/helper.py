import os
import subprocess
from base64 import b64encode


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
