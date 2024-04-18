###### OS / Systems
from calendar import c
from doctest import OutputChecker
import os
import sys
from this import d

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
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

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent
from session import Session
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
### planner plan is passed as a property, e.g.
# "plan": [ 
#     ["user","a"],
#     ["a","b"],
#     ["a","c"],
#     ["b","d"],
#     ["c","d"]
# ]
# in the above agents can be further specified with a suffix that represents an identified, for example: a:1, a:2
#
# where the plan is to take data in user stream and pass it on to agent a first, 
# next, agent a's result is then passed on to agents b and c,
# and lastly agent d will take results from b and c to produce it's results
#
class PlannerAgent(Agent):
    def __init__(self, name="PLANNER", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)

        self.initialize_plan()

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        self.initialize_plan()


    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['aggregator'] = True 
        self.properties['aggregator.eos'] = 'NEVER'

    def initialize_plan(self):
      
        plan = {}
        self.plan = plan

        
        canonical2node = {}
        id2node = {}
        
        if 'plan' in self.properties:
            tuples = self.properties['plan']
            
            sources = set()
            destinations = set()
            for tuple in tuples:
                # get canonical src and dst from plan relations: src -> dst
                src = tuple[0]
                dst = tuple[1]

                src_canonical_name = src.split(':')
                dst_canonical_name = dst.split(':')

                # parse agent name, id from canonical name
                src_agent_name = src_canonical_name[0]
                src_agent_ref = '*'
                if len(src_canonical_name) > 1:
                    src_agent_ref = src_canonical_name[1]

                dst_agent_name = dst_canonical_name[0]
                dst_agent_ref = '*'
                if len(dst_canonical_name) > 1:
                    dst_agent_ref = dst_canonical_name[1]

                src_canonical_name = ":".join([src_agent_name, src_agent_ref])
                dst_canonical_name = ":".join([dst_agent_name, dst_agent_ref])

                src_node = None
                if src_canonical_name in canonical2node:
                    src_node = canonical2node[src_canonical_name]
                else:
                    src_node = { 'agent': src_agent_name, 'canonical_name': src_canonical_name, 'id': None, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED' }
                    canonical2node[src_canonical_name] = src_node

                dst_node = None
                if dst_canonical_name in canonical2node:
                    dst_node = canonical2node[dst_canonical_name]
                else:
                    dst_node = { 'agent': dst_agent_name, 'canonical_name': dst_canonical_name, 'id': None, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED' }
                    canonical2node[dst_canonical_name] = dst_node

                src_node['next'].append(dst_node)
                dst_node['prev'].append(src_node)

                if src_canonical_name not in sources:
                    sources.add(src_agent_name)
                if dst_canonical_name not in destinations:
                    destinations.add(dst_agent_name)

            start = sources.difference(destinations)

            plan['start'] = start
            plan['canonical2node'] = canonical2node
            plan['id2node'] = id2node

        return plan

    # node status progression
    # PLANNED, TRIGGERED, STARTED, FINISHED
    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):

        # TODO: Instructions should use TAGs not agent_name
        agent_name = stream.split(':')[0]

        plan = self.plan
        logging.info(plan)
        start = plan['start']
        canonical2node = plan['canonical2node']
        id2node = plan['id2node']
        logging.info("stream {} {}".format(stream, str(id2node)))

        if label == 'EOS':
            if stream in id2node:
                node = id2node[stream]
                node['status'] = 'FINISHED'

                # check if next can run
                nexts = node['next']

                logging.info(plan)
                for next in nexts:
                    proceed = True
                    prevs = next['prev']
                    for prev in prevs:
                        if prev['status'] == 'FINISHED':
                            continue
                        else:
                            proceed = False
                            break

                    if proceed:
                        next_agent_name = next['agent']
                        next_canonical_name = next['canonical_name']

                        # assign an id to keep track
                        next_id = next_agent_name + ":" + str(hex(uuid.uuid4().fields[0]))[2:]
                        next['id'] = next_id
                        id2node[next_id] = next 

                        next['status'] = 'TRIGGERED'

                        ### prepare plan data/instruction 
                        # assign input stream
                        instruction = {}
                        instruction['agent'] = next_agent_name
                        instruction['id'] = next_id
                        instruction['stream'] = stream

                        ### put instruction into plan stream
                        logging.info(plan)
                        return 'INSTRUCTION', instruction, 'json'
            else:
                # doesn't belong to plan
                pass
            

        elif label == 'BOS':
            # if a start node instantiate a plan
            logging.info("checking agent in start {name}{start}".format(name=agent_name,start=str(start)))
            if agent_name in start:
                canonical_name = agent_name + ":" + "*"
                node = canonical2node[canonical_name]
                logging.info(node)
                node['id'] = stream
                node['status'] = 'STARTED'
                id2node[stream] = node
            elif stream in id2node:
                node = id2node[stream]
                node['status'] = 'STARTED'
            else:
                pass

        elif label == 'DATA':
            # nothing to do here, other than setting status
            if stream in id2node:
                node = id2node[stream]
                node['status'] = 'PROCESSING'
    
        return None

class AgentA(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("A", session=session, input_stream=input_stream, processor=processor, properties=properties)

   
    def default_processor(self, stream, id, label, data, dtype=None, properties=None, worker=None):
        if label == 'INSTRUCTION':
            logging.info(label)
            logging.info(id)
            logging.info(data)
            logging.info(properties)
            logging.info(worker)
            logging.info(worker.agent)
            instruction = json.loads(data)
            instruction_agent = instruction['agent']
            assigned_id = instruction['id']
            input_stream = instruction['stream']
            if instruction_agent == self.name:
                worker.agent.create_worker(input_stream, id=assigned_id)
                return 
        elif label == 'EOS':
            # compute stream data
            l = 0
            if worker:
                l = worker.get_data_len('stream')
            time.sleep(4)
            
            # output to stream
            return l
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('stream', data)
    
        return None


class AgentB(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("B", session=session, input_stream=input_stream, processor=processor, properties=properties)

   
    def default_processor(self, stream, id, label, data, dtype=None, properties=None, worker=None):
        if label == 'INSTRUCTION':
            logging.info(label)
            logging.info(id)
            logging.info(data)
            logging.info(properties)
            logging.info(worker)
            logging.info(worker.agent)
            instruction = json.loads(data)
            instruction_agent = instruction['agent']
            assigned_id = instruction['id']
            input_stream = instruction['stream']
            if instruction_agent == self.name:
                worker.agent.create_worker(input_stream, id=assigned_id)
                return 
        elif label == 'EOS':
            # compute stream data
            l = 0
            if worker:
                l = worker.get_data_len('stream')
            time.sleep(4)
            
            # output to stream
            return l
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('stream', data)
    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="PLANNER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', default=False, action=argparse.BooleanOptionalAction)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)
    
    if args.serve:
        # launch agent with parameters, start session
        def launch(*args, **kwargs):
            logging.info("Launching PlannerAgent...")
            logging.info(kwargs)
            agent = PlannerAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching PlannerAgent...")
            logging.info(kwargs)
            agent = PlannerAgent(*args, **kwargs)
            logging.info("Joined session: " + kwargs['session'])
            logging.info("Launched.")
            return kwargs['session']

        # run rpc server
        rpc = RPCServer(args.name, properties=properties)
        rpc.register(launch)
        rpc.register(join)
        rpc.run()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(args.session)
            a = PlannerAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = PlannerAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = PlannerAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()



