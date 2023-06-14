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


class Consumer():
    def __init__(self, name, stream, gid=None, listener=None, properties={}):

        self.name = name
        self.stream = stream
        
        if gid is None:
            gid = uuid.uuid4()
        self.gid = gid 

        self.group = self.name + ":" + str(self.gid)

        if listener is None:
            listener = lambda id, data: print("{id}:{data}".format(id=id, data=data))

        self.listener = listener
        self.properties = properties

        self.threads = []

        self._initialize()

    ###### initialization
    def _initialize(self):
        self._initialize_properties()

    def _initialize_properties(self):
        if 'num_threads' not in self.properties:
            self.properties['num_threads'] = 1

        if 'host' not in self.properties:
            self.properties['host'] = 'localhost'

        if 'port' not in self.properties:
            self.properties['port'] = 6379


    ####### open connection, create group, start threads
    def start(self):
        # logging.info("Starting consumer {c} for stream {s}".format(c=self.name,s=self.stream))
        self.stop_signal = False

        self._start_connection()

        self._start_group()

        self._start_threads()

        logging.info("Started consumer {c} for stream {s}".format(c=self.name,s=self.stream))

    def stop(self):
        logging.info("Stopping consumer {c} for stream {s}".format(c=self.name,s=self.stream))
        self.stop_signal = True

    def wait(self):
        for t in self.threads:
            t.join()

    def _start_connection(self):
        host = self.properties['host']
        port = self.properties['port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def _start_group(self):
        # create group if it doesn't exists, print group info 
        s = self.stream
        g = self.group
        r = self.connection
       
        try:
            # logging.info("Creating group {g}...".format(g=g))
            r.xgroup_create(name=s, groupname=g, id=0)
        except:
            logging.info("Group {g} exists...".format(g=g))

        # self._print_group_info()

    def _print_group_info(self):
        s = self.stream
        g = self.group
        r = self.connection

        logging.info("Group info for stream {s}".format(s=s))
        res = r.xinfo_groups(name=s)
        for i in res:
            logging.info(f"{s} -> group name: {i['name']} with {i['consumers']} consumers and {i['last-delivered-id']}"
                + f" as last read id")

    def get_stream(self):
        return self.stream

    def get_group(self):
        return self.group

    def _consume_stream(self, c):
        s = self.stream
        g = self.group
        r = self.connection
        l = self.listener

        logging.info("[Thread {c}]: starting".format(c=c))
        while(True):
            
            if self.stop_signal:
                break
            
            # check any pending, if so claim
            m = r.xautoclaim(count=1, name=s, groupname=g, consumername=str(c), min_idle_time=10000, justid=False)
    
            if len(m) > 0:
                d = m 
                id = d[0]
                data = d[1]

                # check special token (no data to claim)
                if id == "0-0":
                    pass
                else:
                    logging.info("[Thread {c}]: reclaiming... {id}".format(c=c, id=id))

                    # listen
                    l(id, data)

                    # ack
                    r.xack(s, g, id)
                    continue

            # otherwise read new
            m = r.xreadgroup(count=1, streams={s:'>'}, block=200, groupname=g, consumername=str(c))
            
            if len(m) > 0:
                e = m[0]
                s = e[0]
                d = e[1][0]
                id = d[0]
                data = d[1]

                logging.info("[Thread {c}]: listening... {id} {data}".format(c=c, id=id, data=data))
                
                # listen
                l(id, data)

                # occasionally throw exception (for testing failed threads)
                # if random.random() > 0.5:
                #    print("[Thread {c}]: throwing exception".format(c=c))
                #    raise Exception("exception")          
                
                # ack 
                r.xack(s, g, id)

        logging.info("[Thread {c}]: finished".format(c=c))

    
    def _start_threads(self):
        # start threads
        num_threads = self.properties['num_threads']
        
        for i in range(num_threads):
            t = threading.Thread(target=lambda : self._consume_stream(self.name + "-" + str(i)), daemon=True)
            t.start()
            self.threads.append(t)
            

    def _delete_stream(self):
        s = self.stream
        r = self.connection

        l = r.xread(streams={s:0})
        for _, m in l:
            [ r.xdel( s, i[0] ) for i in m ]




#######################
if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--name', type=str, default='consumer')
   parser.add_argument('--stream', type=str, default='stream')
   parser.add_argument('--threads', type=int, default=1)
   
   args = parser.parse_args()

   # create a listener
   def listener(id, data):
       print("hello {data}".format(data=data))

   c = Consumer(args.name, args.stream, listener=listener)
   c.start()
  

