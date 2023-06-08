###### OS / Systems
import os
import sys

###### 
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class UserAgent(Agent):
    def __init__(self, name, stream, properties={}):
        super().__init__(name, stream, properties=properties)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='USER')
    parser.add_argument('--interactive', type=bool, default=False, action=argparse.BooleanOptionalAction, help="input text interactively (default False)")

    args = parser.parse_args()

    a = UserAgent(args.name, stream=None)
    a.start()

    # write to user stream
    while (True):
        text = ""
        if args.interactive:
            text = input('Enter Text:')
        else:
            text = args.text

        # write to stream 
        a.write(text, type="text")

        if not args.interactive:
            break




