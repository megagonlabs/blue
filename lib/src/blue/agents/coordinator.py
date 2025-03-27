###### Parsers, Formats, Utils
import logging
import uuid
import json


###### Blue
from blue.agent import Agent
from blue.plan import Plan, Status, NodeType
from blue.stream import ControlCode
from blue.utils import uuid_utils


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


##########################
### Agent.CoordinatorAgent
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

        # update status
        plan.set_status(Status.INITED)

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
                    plan.set_node_stream(node_id, stream, save=True)
                    # process stream
                    self.create_worker(stream, input=plan_id)

        ### do regular session listening
        return super().session_listener(message)

    def transform_data(self, input_stream, budget, f, t):
        # TODO: 
        output_stream = input_stream

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

                # set plan status
                plan.set_status(Status.RUNNING, save=True)

                ### set stream status, capture value
                if message.isBOS():
                    plan.set_stream_status(stream, Status.RUNNING, save=True)
                    plan.set_stream_value(stream, [], save=True)
                elif message.isData():
                    v = message.getData()
                    plan.append_stream_value(stream, v, save=True)
                elif message.isEOS():
                    plan.set_stream_status(stream, Status.FINISHED, save=True)

                    # check, update plan status
                    plan.check_status(save=True)
            
                ###  trigger next 
                # identify node
                if message.isBOS():
                    # determine stream output from the agent
                    nodes = plan.get_nodes_by_stream(stream, node_type=[NodeType.AGENT_OUTPUT,NodeType.INPUT])
       
                    node = None
                    if len(nodes) == 1:
                        node = nodes[0]
                    
                    if node is None:
                        return 

                    node_id = node['id']

                    #### from
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

                    #### next
                    next_nodes = plan.get_next_nodes(node_id)
    
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

                        if t is None:
                            continue

                        input_stream = stream

                        # transform data utilizing planner/optimizers, if necessary
                        budget = worker.session.get_budget()

                        # set input stream to stream
                        input_stream = self.transform_data(stream, budget, f, t)

                        # set next node stream
                        plan.set_node_stream(next_node_id, input_stream, save=True)
                       
                        # write an EXECUTE_AGENT instruction
                        if input_stream:
                            # execute agent
                            if to_agent:
                                context = plan.get_scope() + ":PLAN:" + plan_id
                                to_agent_properties = plan.get_node_properties(to_agent_id)
                                # issue instruction
                                worker.write_control(ControlCode.EXECUTE_AGENT, {"agent": to_agent, "context": context, "properties": to_agent_properties, "inputs": {to_agent_param: input_stream}})
                            elif to_output:
                                # nothing to do
                                pass

                elif message.isEOS():
                    # set node values from finished stream 
                    nodes = plan.get_nodes_by_stream(stream, node_type=NodeType.OUTPUT)

                    for node in nodes:
                        node_id = node['id']
                        plan.set_node_value_from_stream(node_id, save=True)

                    # check, update plan status
                    plan.check_status(save=True)
                    

        return None