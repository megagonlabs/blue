###### Parsers, Formats, Utils
import logging
import uuid
import json


###### Blue
from blue.agent import Agent
from blue.stream import ControlCode
from blue.data.planner import DataPlanner
from blue.data.pipeline import DataPipeline
from blue.utils import uuid_utils


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


##########################
### Agent.CoordinatorAgent
#
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
            plan["id"] = uuid_utils.create_uuid()
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

        # # plan status
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
            src_canonical_name = step[0]
            dst_canonical_name = step[1]

            # split into <agent>.<param>, is possible
            src_canonical_name_list = src_canonical_name.split('.')
            dst_canonical_name_list = dst_canonical_name.split('.')

            if len(src_canonical_name_list) == 1:
                input_name = src_canonical_name_list[0]
            else:
                # parse agent name, id from canonical name
                src_agent_name = src_canonical_name_list[0]
                src_agent_param = src_canonical_name_list[1]

            if len(dst_canonical_name_list) == 1:
                output_name = dst_canonical_name_list[0]
            else:
                dst_agent_name = dst_canonical_name_list[0]
                dst_agent_param = dst_canonical_name_list[1]

            ### SOURCE
            src_id = None
            src_node = None

            if src_canonical_name in canonical2id:
                src_id = canonical2id[src_canonical_name]
                src_node = id2node[src_id]
            else:
                src_id = uuid_utils.create_uuid()

                
                if len(src_canonical_name_list) == 1:
                    # create input node
                    src_node = {'input': input_name, 'canonical_name': src_canonical_name, 'id': src_id, 'next': [], 'prev': [], 'status': 'PLANNED'}
                else:
                    # create source agent node
                    src_node = {'agent': src_agent_name, 'param': src_agent_param, 'canonical_name': src_canonical_name, 'id': src_id, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED'}
                
                canonical2id[src_canonical_name] = src_id
                id2node[src_id] = src_node

            ### DESTINATION
            dst_id = None
            dst_node = None

            if dst_canonical_name in canonical2id:
                dst_id = canonical2id[dst_canonical_name]
                dst_node = id2node[dst_id]
            else:
                dst_id = uuid_utils.create_uuid()

                if len(dst_canonical_name_list) == 1:
                    # create output node
                    dst_node = {'output': output_name, 'canonical_name': dst_canonical_name, 'id': dst_id, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED'}
                else:
                    # create destination agent node
                    dst_node = {'agent': dst_agent_name, 'param': dst_agent_param, 'canonical_name': dst_canonical_name, 'id': dst_id, 'next': [], 'prev': [], 'params': {}, 'status': 'PLANNED'}
                
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
                        # TODO: outputs will also be included in canonical2id
                        # TODO: when all outputs are completed, plan status is FINISHED
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

        # context = {}
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
        # pipeline = DataPipeline(id=pid, properties=self.properties)
        # output_data = pipeline.execute(plan, budget)

        # # # persist data to stream
        # output_stream = self.persist_stream_data(output_data)

        # # TODO: update session budget

        # # TODO: OVERRIDE TEMPORARILY
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

            # if stream is of output variable, store value/stream if desired 
            if message.isBOS():
                # # set planned to False
                worker.set_data(plan_id + ".status.planned." + stream, False)
                # set runnning to True
                worker.set_data(plan_id + ".status.running." + stream, True)

                # update node status
                node_id = worker.get_data(plan_id + ".stream2id." + stream)
                worker.set_data(plan_id + ".id2node." + node_id + ".status", "RUNNING")
            elif message.isEOS():
                # # set running to False
                worker.set_data(plan_id + ".status.running." + stream, False)
                # set finished to True
                worker.set_data(plan_id + ".status.finished." + stream, True)

                # update node status
                node_id = worker.get_data(plan_id + ".stream2id." + stream)
                worker.set_data(plan_id + ".id2node." + node_id + ".status", "FINISHED")

                context_scope = worker.get_data(plan_id + ".context.scope")

                # get from agent, if possible
                from_agent = worker.get_data(plan_id + ".id2node." + node_id + ".agent")
                from_agent_param = worker.get_data(plan_id + ".id2node." + node_id + ".param")

                # start nexts agents
                next_node_ids = worker.get_data(plan_id + ".id2node." + node_id + ".next")
  
                for next_node_id in next_node_ids:

                    # if next node is output
                    # store value, set status to FINISHED
                    # else if agent, start 
                    next_agent = worker.get_data(plan_id + ".id2node." + next_node_id + ".agent")
                    next_agent_param = worker.get_data(plan_id + ".id2node." + next_node_id + ".param")

                   
                    output_stream = stream

                    if from_agent:
                        # transform data utilizing planner/optimizers, if necessary
                        budget = worker.session.get_budget()
                        output_stream = self.transform_data(stream, budget, from_agent, from_agent_param, next_agent, next_agent_param)

                    # create an EXECUTE_AGENT instruction
                    if output_stream:
                        context = context_scope + ":PLAN:" + plan_id
                        worker.write_control(ControlCode.EXECUTE_AGENT, {"agent": next_agent, "context": context, "properties": {}, "inputs": {next_agent_param: output_stream}})

            else:
                pass

        return None