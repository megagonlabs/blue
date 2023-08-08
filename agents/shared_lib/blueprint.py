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

###### Backend, Databases
import redis

###### Threads
import threading
import concurrent.futures

# set log level
logging.getLogger().setLevel(logging.INFO)

class BluePrint():
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)


    def _initialize_properties(self):
        self.properties = {}
        self.properties['host'] = 'localhost'
        self.properties['port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]


    ####### open connection, create group, start threads
    def start(self):
        logging.info("Starting architecture {name}".format(name=self.name))

        logging.info("Started architecture {name}".format(name=self.name))

    def stop(self):
        logging.info("Stopping architecture {name}".format(name=self.name))
        


  

#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str)
    parser.add_argument('--properties', type=str)
   
    args = parser.parse_args()

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    bp = BluePrint(args.name, properties=properties)

    
    bp.add_agent()
    bp.start()
  

