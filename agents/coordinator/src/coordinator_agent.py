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
sys.path.append('./lib/data_planner/')
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
from agent import Agent, AgentFactory
from data_planner import DataPlanner
from pipeline import Pipeline
from session import Session
from message import Message, MessageType, ContentType, ControlCode

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


#######################
### planner plan is passed as a property, e.g.
# "plan": [
#     ["user.text","a.default"],
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
class CoordinatorAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "COORDINATOR"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # coordinator is not instructable
        self.properties['instructable'] = False

        # if plan is fixed, in properties
        if 'plan' in self.properties:
            plan = self.properties['plan']
            self.initialize_plan(plan)

    def _initialize_properties(self):
        super()._initialize_properties()

        listeners = {}
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        self.properties['listens'] = listeners
        default_listeners['includes'] = ['PLAN']
        default_listeners['excludes'] = []

    def initialize_plan(self, plan, worker=None):

        # create worker if None
        if worker == None:
            # TODO: Create worker
            return

        # init id if None
        if 'id' not in plan:
            plan["id"] = create_uuid()
        plan_id = plan["id"]

        # add plan to list to monitor
        plans = worker.get_data("plans")
        if plans is None:
            worker.set_data("plans", {})
        worker.set_data("plans." + plan_id, True)

        # context: scope, streams
        context = plan['context']
        context_scope = context['scope']
        # plan steps
        steps = plan['steps']

        # node access by name, stream
        canonical2id = {}
        plan["canonical2id"] = canonical2id
        stream2id = {}
        plan["stream2id"] = stream2id
        id2node = {}
        plan["id2node"] = id2node

        # plan status
        status = {}
        planned = {}
        running = {}
        finished = {}
        plan['status'] = status
        status['planned'] = planned
        status['running'] = running
        status['finished'] = finished

        # process steps
        for step in steps:
            # get canonical src and dst from plan relations: src -> dst
            src = step[0]
            dst = step[1]

            src_canonical_name = src.split('.')
            dst_canonical_name = dst.split('.')

            # parse agent name, id from canonical name
            src_agent_name = src_canonical_name[0]
            src_agent_param = src_canonical_name[1]

            dst_agent_name = dst_canonical_name[0]
            dst_agaent_param = dst_canonical_name[1]

            src_canonical_name = ".".join([src_agent_name, src_agent_param])
            dst_canonical_name = ".".join([dst_agent_name, dst_agaent_param])

            src_id = None
            src_node = None
            if src_canonical_name in canonical2id:
                src_id = canonical2id[src_canonical_name]
                src_node = id2node[src_id]
            else:
                src_id = create_uuid()

                src_node = {'agent': src_agent_name, 'param': src_agent_param, 'canonical_name': src_canonical_name, 'id': src_id, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED'}
                canonical2id[src_canonical_name] = src_id
                id2node[src_id] = src_node

            dst_id = None
            dst_node = None
            if dst_canonical_name in canonical2id:
                dst_id = canonical2id[dst_canonical_name]
                dst_node = id2node[dst_id]
            else:
                dst_id = create_uuid()

                dst_node = {'agent': dst_agent_name, 'param': dst_agaent_param, 'canonical_name': dst_canonical_name, 'id': dst_id, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED'}
                canonical2id[dst_canonical_name] = dst_id
                id2node[dst_id] = dst_node

            src_node['next'].append(dst_node['id'])
            dst_node['prev'].append(src_node['id'])

        plan['canonical2id'] = canonical2id
        plan['id2node'] = id2node

        # process context.streams
        streams = context['streams']
        for canonicalname in streams:
            stream = streams[canonicalname]
            id = canonical2id[canonicalname]
            stream2id[stream] = id

            planned[stream] = True


        # persist plan data to agent memory
        worker.set_data(plan_id, plan)

        ### start executing plan from streams
        # create workers to planned streams to monitor progress
        for stream in planned:
            self.create_worker(stream, input=plan_id)

    def verify_plan(self, plan):
        if type(plan) == dict:
            if 'id' not in plan:
                return None
            if 'steps' not in plan:
                return None
            if 'context' not in plan:
                return None
            context = plan['context']
            if 'scope' not in context:
                return None 
            if 'streams' not in context:
                return None
        else:
            return None
        return plan

    def session_listener(self, message):
        ### check if stream is in stream watch list
        if message.getCode() == ControlCode.ADD_STREAM:
            stream = message.getArg("stream")

            # check if stream is part of plan
            plans = self.get_data('plans')
            if plans:
                for plan_id in plans:
                    context_scope = self.get_data(plan_id + ".context.scope")
                    prefix = context_scope + ":PLAN:" + plan_id + ":"
                    canonical2id = self.get_data(plan_id + ".canonical2id")
                    id2node = self.get_data(plan_id + ".id2node")
                    if stream.find(prefix) == 0:
                        s = stream[len(prefix) :]
                        ss = s.split(":")
                        agent = ss[0]
                        param = ss[3]
                        canonical_name = agent + "." + param
                        if canonical_name in canonical2id:
                            id = canonical2id[canonical_name]
                            self.set_data(plan_id + ".stream2id." + stream, id)
                            # create worker
                            self.create_worker(stream, input=plan_id)

        ### do regular session listening
        return super().session_listener(message)

    def transform_data(self, input_stream, budget, from_agent, from_agent_param, to_agent, to_agent_param):
        # logging.info("TRANSFORM DATA:")
        # logging.info(from_agent + "." + from_agent_param)
        # logging.info(to_agent + "." + to_agent_param)
        # logging.info("BUDGET:")
        # logging.info(json.dumps(budget, indent=3))

        context = {}
        # TODO: get registry info on from_agent, from_agent_param

        # TODO: get registry info on to_agent, to_agent_param

        # TODO: TEMPORARY

        # fetch data from stream
        # input_data = self.fetch_stream_data(input_stream)

        # # TODO: call data planner, plan, optimize given budget
        # pid = str(hex(uuid.uuid4().fields[0]))[2:]
        # dp = DataPlanner(id=pid, properties=self.properties)
        # plan = dp.plan(input_data, "TRANSFORM", context)
        # plan = dp.optimize(plan, budget)

        # # TODO: execute plan, update budget
        # pipeline = Pipeline(id=pid, properties=self.properties)
        # output_data = pipeline.execute(plan, budget)

        # # persist data to stream
        # output_stream = self.persist_stream_data(output_data)

        # TODO: update session budget

        # TODO: OVERRIDE TEMPORARILY
        output_stream = input_stream

        return output_stream

    # TODO: fetch data from stream
    def fetch_stream_data(self, input_stream):
        # get input data 
        input_data = None 

        return input_data
    
    # TODO: persist data to stream
    def persist_stream_data(self, input_data):
        # return output stream
        output_stream = None

        return output_stream 
    
    # node status progression
    # PLANNED, TRIGGERED, STARTED, FINISHED
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        if input == "DEFAULT":
            # new plan
            stream = message.getStream()

            if message.isData():
                p = message.getData()

                plan = self.verify_plan(p)
                if plan:
                    # start plan
                    self.initialize_plan(plan, worker=worker)
        else:
            # process a plan
            plan_id = input
            stream = message.getStream()

            if message.isBOS():
                # set planned to False
                worker.set_data(plan_id + ".status.planned." + stream, False)
                # set runnning to True
                worker.set_data(plan_id + ".status.running." + stream, True)

                # update node status
                node_id = worker.get_data(plan_id + ".stream2id." + stream)
                worker.set_data(plan_id + ".id2node." + node_id + ".status", "RUNNING")
            elif message.isEOS():
                # set running to False
                worker.set_data(plan_id + ".status.running." + stream, False)
                # set finished to True
                worker.set_data(plan_id + ".status.finished." + stream, True)

                # update node status
                node_id = worker.get_data(plan_id + ".stream2id." + stream)
                worker.set_data(plan_id + ".id2node." + node_id + ".status", "FINISHED")

                context_scope = worker.get_data(plan_id + ".context.scope")
                # get from agent
                from_agent = worker.get_data(plan_id + ".id2node." + node_id + ".agent")
                from_agent_param = worker.get_data(plan_id + ".id2node." + node_id + ".param")

                # start nexts agents
                next_node_ids = worker.get_data(plan_id + ".id2node." + node_id + ".next")
  
                for next_node_id in next_node_ids:
                    next_agent = worker.get_data(plan_id + ".id2node." + next_node_id + ".agent")
                    next_agent_param = worker.get_data(plan_id + ".id2node." + next_node_id + ".param")

                    # transform data utilizing planner/optimizers, if necessary
                    budget = worker.session.get_budget()
                    output_stream = self.transform_data(stream, budget, from_agent, from_agent_param, next_agent, next_agent_param)

                    # create an EXECUTE_AGENT instruction
                    if output_stream:
                        context_cid = context_scope + ":PLAN:" + plan_id
                        worker.write_control(ControlCode.EXECUTE_AGENT, {"agent": next_agent, "context": context_cid, "params": {next_agent_param: output_stream}})

            else:
                pass

        # start = plan['start']
        # canonical2node = plan['canonical2node']
        # stream2node = plan['stream2node']
        # logging.info("stream {} {}".format(stream, str(stream2node)))

        # if message.isEOS():
        #     if stream in stream2node:
        #         node = stream2node[stream]
        #         node['status'] = 'FINISHED'

        #         # check if next can run
        #         nexts = node['next']

        #         logging.info(plan)
        #         for next in nexts:
        #             proceed = True
        #             prevs = next['prev']
        #             for prev in prevs:
        #                 if prev['status'] == 'FINISHED':
        #                     continue
        #                 else:
        #                     proceed = False
        #                     break

        #             if proceed:
        #                 next_agent_name = next['agent']
        #                 next_canonical_name = next['canonical_name']

        #                 # assign an id to keep track
        #                 next_id = next_agent_name + ":" + str(hex(uuid.uuid4().fields[0]))[2:]
        #                 next['id'] = next_id
        #                 stream2node[next_id] = next

        #                 next['status'] = 'TRIGGERED'

        #                 ### prepare plan data/instruction
        #                 args = {}
        #                 args['agent'] = next_agent_name
        #                 input = {}
        #                 input["DEFAULT"] = stream # TODO: Is this correct?
        #                 args["input"] = input
        #                 args['context'] = ""

        #                 ### put instruction into plan stream
        #                 logging.info(plan)
        #                 return Message(Message.MessageType.CONTROL, {"code": ControlCode.EXECUTE_AGENT, "args": args}, ContentType.JSON)
        #     else:
        #         # doesn't belong to plan
        #         pass

        # elif message.isBOS():
        #     # if a start node instantiate a plan
        #     logging.info("checking agent in start {name}{start}".format(name=agent_name,start=str(start)))
        #     if agent_name in start:
        #         canonical_name = agent_name + ":" + "*"
        #         node = canonical2node[canonical_name]
        #         logging.info(node)
        #         node['id'] = stream
        #         node['status'] = 'STARTED'
        #         stream2node[stream] = node
        #     elif stream in stream2node:
        #         node = stream2node[stream]
        #         node['status'] = 'STARTED'
        #     else:
        #         pass

        # elif message.isData():
        #     # nothing to do here, other than setting status
        #     if stream in stream2node:
        #         node = stream2node[stream]
        #         node['status'] = 'PROCESSING'

        return None


class AgentA(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "A"
        super().__init__(**kwargs)

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if message.getCode() == ControlCode.EXECUTE_AGENT:

            instruction_agent = message.getArg("agent")
            input_stream = message.getArg['stream']
            if instruction_agent == self.name:
                worker.agent.create_worker(input_stream, input="DEFAULT")
                return
        elif message.isEOS():
            # compute stream data
            l = 0
            if worker:
                l = worker.get_data_len('stream')
            time.sleep(4)

            # output to stream
            return l
        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream', [])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            logging.info(data)

            if worker:
                worker.append_data('stream', data)

        return None


class AgentB(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "B"
        super().__init__(**kwargs)

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if message.getCode() == ControlCode.EXECUTE_AGENT:

            instruction_agent = message.getArg("agent")
            input_stream = message.getArg['stream']
            if instruction_agent == self.name:
                worker.agent.create_worker(input_stream, input="DEFAULT")
                return
        elif message.isEOS():
            # compute stream data
            l = 0
            if worker:
                l = worker.get_data_len('stream')
            time.sleep(4)

            # output to stream
            return l
        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream', [])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            logging.info(data)

            if worker:
                worker.append_data('stream', data)

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="COORDINATOR", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

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
        platform = args.platform

        af = AgentFactory(_class=CoordinatorAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = CoordinatorAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = CoordinatorAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
