###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/service/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')

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
from utils import json_utils
from utils import string_utils
import copy

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from service import Service

##### Agent specifc
import dspy

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")




#######################    
class ExtractOperator(dspy.Signature):
    """Given a natural language text, tag the named entities with [MEN] and [/MEN]"""

    text = dspy.InputField(desc="natural language text without entity annotations")
    annotated_text = dspy.OutputField(desc="natural language text with annotations", prefix='')

### dspy extact operator
dspy_operator = dspy.Predict(ExtractOperator)
llm = dspy.OpenAI(model='gpt-4o')

### dspy configuration
dspy.settings.configure(lm=llm, rm=None)


class DSPyService(Service):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "DSPY"
        super().__init__(**kwargs)

    def default_handler(self, message, properties=None, websocket=None):
        # process message
        message = json.loads(message)
        budget = message['budget']
        input = message['input']

        # prepare output, return
        output = dspy_operator(text=input)

        result = {}
        result['output'] = output.annotated_text

        return result


if __name__ == "__main__":
    logging.info('starting....')
 

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="DSPY")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--platform", type=str, default="default")

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties

    print(args)
    if p:
        # decode json
        properties = json.loads(p)
        print("properties:")
        print(json.dumps(properties, indent=3))
        print("---")

    # create service
    prefix = "PLATFORM:" + args.platform + ":SERVICE"
    s = DSPyService(name=args.name, prefix=prefix, properties=properties)

    # run
    asyncio.run(s.start_listening_socket())
    