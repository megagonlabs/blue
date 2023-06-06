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
class MyAgent(Agent):
    def __init__(self, name, stream, processor=None, properties={}):
        super().__init__(name, stream, processor=processor, properties=properties)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='AGENT')
    parser.add_argument('--input_stream', type=str, default='input')
 
    args = parser.parse_args()

    stream_data = []

    # sample func to process data
    def processor(id, event, data):
        if event == 'EOS':
            # print all data received from stream
            print(stream_data)

            # compute stream data
            l = len(stream_data)
            time.sleep(4)
            
            # output to stream
            return l
           
        elif event == 'DATA':
            # store data value
            stream_data.append(data)
        
        return None

    a = MyAgent(args.name, args.input_stream, processor=processor)
    a.start()



