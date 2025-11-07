###### Parsers, Formats, Utils
import logging
import uuid
import json


###### Blue
from blue.agent import Agent
from blue.agents.registry import AgentRegistry
from blue.platform import Platform
from blue.agents.plan import AgenticPlan, Status, NodeType
from blue.stream import ControlCode
from blue.utils import uuid_utils, json_utils

# from blue.data.planner import DataPlanner, TaskType
# from blue.data.pipeline import DataPipeline


##########################
### Agent.CoordinatorAgent
#
class CoordinatorAgent(Agent):
    """Agent that coordinates the execution of plans involving multiple agents.

    This agent listens for incoming plans, initializes and manages their execution by coordinating
    the involved agents, and tracks the progress of each plan, tracking streams announced in the session streams and
    invoking EXECUTE_AGENT commands as needed.

    Plans are represented using the AgenticPlan class, which defines the structure and flow of tasks to be executed by various agents.

    Properties (in addition to Agent properties):
    ----------
    This agent does not have additional properties beyond those inherited from the base Agent class.

    Inputs:
    - DEFAULT: Listens for incoming plans tagged with PLAN.

    Outputs:
    - DEFAULT: Outputs instructions, tagged as `INSTRUCTION` and `HIDDEN`.

    """

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "COORDINATOR"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        """Initialize the agent with properties.

        Parameters:
            properties (dict): Properties to initialize the agent with.
        """
        super()._initialize(properties=properties)

        # coordinator is not instructable
        self.properties['instructable'] = False

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the agent. DEFAULT input includes listeners for tag PLAN."""
        self.add_input("DEFAULT", description="Plan to coordinate", includes=["PLAN"])

    def _initialize_outputs(self):
        """Initialize outputs for the agent. DEFAULT output is tagged as INSTRUCTION and HIDDEN."""
        self.add_output("DEFAULT", description="Instructions to follow", tags=["INSTRUCTION", "HIDDEN"])

    def _start(self):
        """Start the coordinator agent, initializing the platform and agent registry."""
        super()._start()

        # initialize platform
        self._init_platform()

        # initialize registry
        self._init_registry()

        self.plans = {}

    def _init_platform(self):
        """Initialize the platform for the coordinator agent."""
        # create instance of platform
        platform_id = self.properties["platform.name"]
        self.platform = Platform(id=platform_id, properties=self.properties)

    def _init_registry(self):
        """Initialize the agent registry for the coordinator agent."""
        # create instance of agent registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id

        self.registry = AgentRegistry(id=self.properties['agent_registry.name'], prefix=prefix, properties=self.properties)

    def initialize_plan(self, plan, worker=None):
        """Initialize and start executing a plan.

        Parameters:
            plan (AgenticPlan): The plan to be executed.
            worker: The worker handling the execution of the plan.
        """

        # get plan id
        plan_id = plan.get_id()

        # set plan to track
        self.plans[plan_id] = plan

        # update status
        plan.set_status(Status.INITED)

        # add agents to session
        agents = plan.get_agents()
        for agent_id in agents:
            agent = plan.get_agent(agent_id)
            agent_canonical_name = agent.get_data('canonical_name')
            agent_properties = agent.get_properties()
            logging.info("Adding agent to session...")
            # extract sid from cid
            session_sid = uuid_utils.extract_sid(self.session.cid)
            logging.info("Session: " + str(session_sid))
            logging.info("Agent: " + agent_canonical_name)
            logging.info("Properties: " + json.dumps(agent_properties))

            agent_properties_from_registry = self.registry.get_agent_properties(agent_canonical_name, recursive=True, include_params=True)
            agent_properties = json_utils.merge_json(agent_properties_from_registry, agent_properties)

            self.platform.join_session(session_sid, self.properties['agent_registry.name'], agent_canonical_name, agent_properties)

        # process data in streams
        streams = plan.get_streams()

        for stream_id in streams:
            # plan existing streams for inputs/outputs processing
            plan.set_stream_status(stream_id, Status.PLANNED)

            # process nodes with streams
            stream = plan.get_stream(stream_id)
            if stream:
                stream_label = stream.get_data("label")
                self.create_worker(stream_label, input=plan_id)

    def get_plan_progress(self, plan):
        """
        Get the progress of a plan as a float between 0 and 1.

        Parameters:
            plan (AgenticPlan): The plan to get the progress of.

        Returns:
            float: The progress of the plan as a float between 0 and 1.
        """
        num_connections = plan.count_nodes(filter_hasPrev=True)
        num_finished_streams = plan.count_streams(filter_status=[Status.FINISHED])
        return num_finished_streams / num_connections

    def session_listener(self, message):
        """Listen to session messages and handle stream announcements.

        Parameters:
            message: The session message to process.

        """
        ### check if stream is in stream watch list
        if message.getCode() == ControlCode.ADD_STREAM:
            stream = message.getArg("stream")

            # check if stream is part of a plan being tracked
            plan_ids = list(self.plans.keys())
            for plan_id in plan_ids:
                plan = self.plans[plan_id]
                # check if there is a matching node for stream
                node = plan.match_stream(stream)
                if node:
                    node_id = node.get_id()
                    # assign stream to node
                    plan.set_node_stream(node_id, stream)
                    # process stream
                    self.create_worker(stream, input=plan_id)

        ### do regular session listening
        return super().session_listener(message)

    def transform_data(self, input_stream, budget, f, t):
        """Transform data from input stream to output stream based on the plan.

        Currently a placeholder that returns the input stream as the output stream.

        Parameters:
            input_stream: The input stream to transform data from.
            budget: The budget for the transformation.
            f: The from node (can be input or agent output).
            t: The to node (can be output or agent input).

        Returns:
            The output stream after transformation.
        """
        from_input = None
        from_agent = None
        from_agent_param = None
        to_agent = None
        to_agent_param = None
        to_output = None

        if type(f) == tuple:
            from_agent, from_agent_param = f
        else:
            from_input = f

        if type(t) == tuple:
            to_agent, to_agent_param = t
        else:
            to_output = t

        # self.logger.info("TRANSFORM DATA:")
        # self.logger.info(from_agent + "." + from_agent_param)
        # self.logger.info(to_agent + "." + to_agent_param)
        # self.logger.info("BUDGET:")
        # self.logger.info(json.dumps(budget, indent=3))

        context = {}
        # TODO: get registry info on from_agent, from_agent_param

        # TODO: get registry info on to_agent, to_agent_param

        # TODO: TEMPORARY

        # fetch data from stream
        # input_data = self.fetch_stream_data(input_stream)

        # # TODO: call data planner, plan, optimize given budget
        # pid = uuid_utils.create_uuid()
        # dp = DataPlanner(id=pid, properties=self.properties)
        # plan = dp.plan(input_data, TaskType.DATA_TRANSFORM, context)
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

    def plan_synchronizer(self, plan, path, key, value):
        """Synchronize plan changes by updating the plan in the coordinator agent's data store.

        Parameters:
            plan (AgenticPlan): The plan being synchronized.
            path (str): The JSON path of the change.
            key (str): The key of the change.
            value: The value of the change.
        """
        # remove $. from path + key
        canonical_key = path + "." + key
        self.set_data(canonical_key[2:], value)

    # node status progression
    # PLANNED, TRIGGERED, STARTED, FINISHED
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the coordinator agent, handling plan execution and stream management.

        Parameters:
            message: The message to process.
            input: The input stream label.
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """
        if input == "DEFAULT":
            # new plan
            stream = message.getStream()

            if message.isData():
                p = message.getData()

                plan = None
                try:
                    plan = AgenticPlan.from_dict(p)
                except Exception:
                    self.logger.info("Error reading valid plan")

                if plan:
                    # synchronize
                    plan.synchronizer = lambda path, key, value: self.plan_synchronizer(plan, path, key, value)
                    plan.auto_sync = True
                    plan.synchronize()

                    # start plan
                    self.initialize_plan(plan, worker=worker)
                    plan_id = plan.get_id()
                    # status
                    worker.write_progress(progress_id=plan_id, label='Initialized', value=0.0)

        else:
            # get stream
            stream = message.getStream()

            # process a plan
            plan_id = input

            if plan_id in self.plans:
                plan = self.plans[plan_id]

                # set plan status
                plan.set_status(Status.RUNNING)

                ### set stream status, capture value
                if message.isBOS():
                    plan.set_stream_status(stream, Status.RUNNING)
                    plan.set_stream_value(stream, [])
                elif message.isData():
                    v = message.getData()
                    plan.append_stream_value(stream, v)
                elif message.isEOS():
                    plan.set_stream_status(stream, Status.FINISHED)

                    # check, update plan status
                    plan.check_status()

                ###  trigger next
                # identify node
                if message.isBOS():
                    # determine stream output from the agent
                    nodes = plan.get_nodes_by_stream(stream, node_type=[NodeType.AGENT_OUTPUT, NodeType.INPUT])

                    node = None
                    if len(nodes) == 1:
                        node = nodes[0]

                    if node is None:
                        return

                    node_id = node.get_id()

                    #### from
                    f = None
                    from_input = None
                    from_agent = None
                    from_agent_param = None

                    # if from an agent output capture
                    if plan.get_node_type(node_id) == NodeType.AGENT_OUTPUT:
                        from_agent_node = plan.get_node_agent(node_id)
                        from_agent = from_agent_node.get_data('canonical_name')
                        from_agent_param = node.get_data('name')
                        f = (from_agent, from_agent_param)
                    elif plan.get_node_type(node_id) == NodeType.INPUT:
                        from_input = node.get_label()
                        f = from_input

                    #### next
                    next_nodes = plan.get_next_nodes(node_id)

                    for next_node in next_nodes:
                        next_node_id = next_node.get_id()

                        # to
                        t = None
                        to_output = None
                        to_agent = None
                        to_agent_node = None
                        to_agent_id = None
                        to_agent_param = None

                        if plan.get_node_type(next_node_id) == NodeType.AGENT_INPUT:
                            to_agent_node = plan.get_node_agent(next_node_id)
                            to_agent = to_agent_node.get_data('canonical_name')
                            to_agent_id = to_agent_node.get_id()
                            to_agent_param = next_node.get_data('name')
                            t = (to_agent, to_agent_param)
                        elif plan.get_node_type(next_node_id) == NodeType.OUTPUT:
                            to_output = next_node.get_label()
                            t = to_output

                        if t is None:
                            continue

                        input_stream = stream

                        # transform data utilizing planner/optimizers, if necessary
                        budget = worker.session.get_budget()

                        # override output stream if data is transformed
                        input_stream = self.transform_data(stream, budget, f, t)

                        # set next node stream
                        plan.set_node_stream(next_node_id, input_stream)

                        # write an EXECUTE_AGENT instruction
                        if input_stream:
                            # execute agent
                            if to_agent:
                                context = plan.get_scope() + ":PLAN:" + plan_id
                                # get agent properties from registry
                                to_agent_properties = self.registry.get_agent_properties(to_agent, recursive=True, include_params=True)
                                to_agent_plan_properties = plan.get_agent_properties(to_agent_id)
                                to_agent_properties = json_utils.merge_json(to_agent_properties, to_agent_plan_properties)
                                # issue instruction
                                worker.write_control(
                                    ControlCode.EXECUTE_AGENT, {"agent": to_agent, "context": context, "properties": to_agent_properties, "inputs": {to_agent_param: input_stream}}
                                )
                                # progress
                                worker.write_progress(progress_id=plan_id, label='Executing: ' + to_agent, value=self.get_plan_progress(plan))
                            elif to_output:
                                # nothing to do
                                pass

                elif message.isEOS():
                    # set node values from finished stream
                    nodes = plan.get_nodes_by_stream(stream, node_type=NodeType.OUTPUT)

                    for node in nodes:
                        node_id = node.get_id()
                        plan.set_node_value_from_stream(node_id)

                    # check, update plan status
                    plan_status = plan.check_status()

                    if plan_status == Status.FINISHED:
                        worker.write_progress(progress_id=plan_id, label='Finished', value=1.0)

        return None
