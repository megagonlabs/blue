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

        self.properties = properties
       
        self._initialize()

    ###### initialization
    def _initialize(self):
        self._initialize_properties()

    def _initialize_properties(self):
        pass


    ####### open connection, create group, start threads
    def start(self):
        logging.info("Starting architecture {name}".format(name=self.name))

        logging.info("Started architecture {name}".format(name=self.name))

    def stop(self):
        logging.info("Stopping architecture {name}".format(name=self.name))
        

  

#######################
if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--name', type=str, default='consumer')
   
   args = parser.parse_args()

   bp = BluePrint(args.name)
   bp.start()
  

