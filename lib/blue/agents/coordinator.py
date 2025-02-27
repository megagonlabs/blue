###### Parsers, Formats, Utils
import logging
import uuid
import json


###### Blue
from blue.agent import Agent
from blue.plan import Plan, Status, NodeType
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


    def _initialize_properties(self):
        super()._initialize_properties()

        listeners = {}
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        self.properties['listens'] = listeners
        default_listeners['includes'] = ['PLAN']
        default_listeners['excludes'] = []

    def _start(self):
        super()._start()

        self.plans = {}

    def initialize_plan(self, plan, worker=None):

        # get plan id
        plan_id = plan.id

        # set plan to track
        self.plans[plan_id] = plan

        # save plan 
        plan.save()

        # process data instreams
        streams = plan.get_streams()

        for stream in streams:
            # plan existing streams for inputs/outputs processing
            plan.set_stream_status(stream, Status.PLANNED, save=True)

            # process nodes with streams 
            self.create_worker(stream, input=plan_id)

    def session_listener(self, message):
        ### check if stream is in stream watch list
        if message.getCode() == ControlCode.ADD_STREAM:
            stream = message.getArg("stream")

            # check if stream is part of a plan being tracked
            for plan_id in self.plans:
                plan  = self.plans[plan_id]
                # check if there is a matching node for stream
                node = plan.match_stream(stream)
                if node:
                    node_id = node['id']
                    # assign stream to node
                    plan.set_node_stream(node_id, stream, status=Status.PLANNED, save=True)
                    # process stream
                    self.create_worker(stream, input=plan_id)

        ### do regular session listening
        return super().session_listener(message)

    def transform_data(self, input_stream, budget, f, t):
        # from_input = None
        # from_agent = None
        # from_agent_param = None
        # to_agent = None
        # to_agent_param = None
        # to_output = None

        # if type(f) == tuple: 
        #     from_agent, from_agent_param = f
        # else:
        #     from_input = f

        # if type(t) == tuple:
        #     to_agent, to_agent_param = t
        # else:
        #     to_output = t

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

                plan = None
                try:
                    plan = Plan.from_json(p)
                except Exception:
                    logging.info("Error reading valid plan")
                    
                if plan:
                    # start plan
                    self.initialize_plan(plan, worker=worker)
        else:
            # get stream
            stream = message.getStream()

            # process a plan
            plan_id = input

            

            if plan_id in self.plans:
                plan = self.plans[plan_id]

                # identify node
                node = plan.get_node_by_stream(stream)
                node_id = node['id']

                # if stream is of output variable, store value/stream if desired 
                if message.isBOS():
                    plan.set_stream_status(stream, Status.RUNNING, save=True)
                    if plan.get_node_type(node_id) == NodeType.AGENT_OUTPUT:
                        plan.set_node_value(node_id, [], save=True)

                    #### next
                    next_nodes = plan.get_next_nodes(node_id)

                    # from
                    f = None
                    from_input = None
                    from_agent = None
                    from_agent_param = None

                    # if from an agent output capture 
                    if plan.get_node_type(node_id) == NodeType.AGENT_OUTPUT:
                        from_agent_node = plan.get_parent_node(node_id)
                        from_agent = from_agent_node['name']
                        from_agent_param = node['name']
                        f = (from_agent, from_agent_param)
                    elif plan.get_node_type(node_id) == NodeType.INPUT:
                        from_input = node['name']
                        f = from_input
    
                    for next_node in next_nodes:

                        next_node_id = next_node['id']

                        # to
                        t = None
                        to_output = None
                        to_agent = None
                        to_agent_node = None
                        to_agent_id = None
                        to_agent_param = None

                        if plan.get_node_type(next_node_id) == NodeType.AGENT_INPUT:
                            to_agent_node = plan.get_parent_node(next_node_id)
                            to_agent = to_agent_node['name']
                            to_agent_id = to_agent_node['id']
                            to_agent_param = next_node['name']
                            t = (to_agent, to_agent_param)
                        elif plan.get_node_type(next_node_id) == NodeType.OUTPUT:
                            to_output = next_node['name']
                            t = to_output

                        output_stream = stream

                        # transform data utilizing planner/optimizers, if necessary
                        budget = worker.session.get_budget()

                        # override output stream with stream from data transformation
                        output_stream = self.transform_data(stream, budget, f, t)

                        # set next node stream
                        plan.set_node_stream(next_node_id, output_stream, save=True)
                       
                        # write an EXECUTE_AGENT instruction
                        if output_stream:
                            # execute agent
                            if to_agent:
                                context = plan.get_scope() + ":PLAN:" + plan_id
                                to_agent_properties = plan.get_node_properties(to_agent_id)
                                worker.write_control(ControlCode.EXECUTE_AGENT, {"agent": to_agent, "context": context, "properties": to_agent_properties, "inputs": {to_agent_param: output_stream}})
                            elif to_output:
                               pass

                elif message.isData():
                    v = message.getData()
                    if plan.get_node_type(node_id) == NodeType.AGENT_OUTPUT:
                        o = plan.get_node_value(node_id)
                        o.append(v)
                        plan.set_node_value(node_id, o, save=True)

                elif message.isEOS():
                    plan.set_stream_status(stream, Status.FINISHED, save=True)

                    # TODO: Copy value to node

                    # TODO: check if plan is complete
                    # set plan status, if completed

        return None