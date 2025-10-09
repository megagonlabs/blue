###### Parsers, Utils
import json
import logging

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.session import Session
from blue.constant import Constant
from blue.utils import dag_utils
from blue.constant import Separator


###############
### Status
class Status(Constant):
    """
    Status of the plan or stream:

    - INACTIVE: Initial state, not yet started.
    - SUBMITTED: Submitted for execution.
    - INITED: Initialized and ready to run.
    - PLANNED: Planned for execution.
    - RUNNING: Currently executing.
    - FINISHED: Execution completed.
    """

    def __init__(self, c):
        super().__init__(c)


Status.INACTIVE = Status("INACTIVE")
Status.SUBMITTED = Status("SUBMITTED")
Status.INITED = Status("INITED")
Status.PLANNED = Status("PLANNED")
Status.RUNNING = Status("RUNNING")
Status.FINISHED = Status("FINISHED")


class NodeType(Constant):
    """
    Type of node in the plan:

    - INPUT: Input node.
    - OUTPUT: Output node.
    - AGENT_INPUT: Input node for an agent.
    - AGENT_OUTPUT: Output node for an agent.
    """

    def __init__(self, c):
        super().__init__(c)


NodeType.INPUT = Constant("INPUT")
NodeType.OUTPUT = Constant("OUTPUT")
NodeType.AGENT_INPUT = Constant("AGENT_INPUT")
NodeType.AGENT_OUTPUT = Constant("AGENT_OUTPUT")


class EntityType(Constant):
    """
    Type of entity in the plan:

    - AGENT: An agent entity.
    - STREAM: A data stream entity.
    """

    def __init__(self, c):
        super().__init__(c)


EntityType.AGENT = Constant("AGENT")
EntityType.STREAM = Constant("STREAM")


##############
### Agentic Plan
#
class AgenticPlan(dag_utils.Plan):
    """Agentic Plan class for defining and managing agentic plans comprised of agents, inputs, outputs, and streams."""

    def __init__(self, scope=None, id=None, label=None, type="AGENTIC_PLAN", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        """Initializes an AgenticPlan instance.

        Parameters:
            scope: The scope of the plan (Session or str).
            id: Unique identifier for the plan.
            label: Human-readable label for the plan.
            type: Type of the plan (default is "AGENTIC_PLAN").
            properties: Additional properties for the plan.
        """
        self.leaves = None
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

        s = scope
        if isinstance(s, Session):
            s = scope.cid

        self._set_scope(s, sync=sync)

    def _init_data(self, sync=None):
        """Initializes the data for the plan, setting up context and status.

        Parameters:
            sync: Whether to synchronize the data immediately.
        """
        super()._init_data(sync=sync)

        self.set_data("context", {"scope": None}, sync=sync)
        self.set_status(Status.INACTIVE, sync=sync)

    # properties
    def _initialize_properties(self, sync=None):
        """Initializes the properties for the plan, including database connectivity.

        Parameters:
            sync: Whether to synchronize the properties immediately.
        """
        super()._initialize_properties(sync=sync)

        # db connectivity
        self.set_property('db.host', 'localhost', sync=sync)
        self.set_property('db.port', 6379, sync=sync)

    # context, scope
    def get_context(self):
        """Retrieves the context of the plan.

        Returns:
            The context dictionary of the plan.
        """
        return self.get_data("context")

    def get_scope(self):
        """Retrieves the scope of the plan.

        Returns:
            The scope of the plan.
        """
        context = self.get_context()
        if 'scope' in context:
            return context['scope']
        else:
            return None

    def _set_scope(self, scope, sync=None):
        """Sets the scope of the plan.

        Parameters:
            scope: The scope of the plan (Session or str).
            sync: Whether to synchronize the scope immediately.
        """
        context = self.get_context()
        context['scope'] = scope

        self.synchronize(key="context.scope", value=scope)

    # status
    def set_status(self, status, sync=None):
        """Sets the status of the plan.

        Parameters:
            status: The status to set for the plan.
            sync: Whether to synchronize the status immediately.
        """
        self.set_data("status", str(status), sync=sync)

    def get_status(self):
        """Retrieves the status of the plan.
        Returns:
            The status of the plan.
        """
        return self.get_data('status')

    #### plan specific nodes, agents
    # inputs, outputs, agents, w/input and output parameters
    def _get_default_label(self, agent, input=None, output=None):
        """Generates a default label for an agent input or output node.

        Parameters:
            agent: The canonical name of the agent.
            input: The name of the input parameter (if applicable).
            output: The name of the output parameter (if applicable).

        Returns:
            A string representing the default label.
        """
        label = agent

        if input:
            label = label + ".INPUT:" + input
        elif output:
            label = label + ".OUTPUT:" + output

        return label

    def define_input(self, label=None, value=None, stream=None, properties={}, sync=None):
        """Defines an input node for the plan.

        Parameters:
            label: The label for the input node.
            value: The value for the input node.
            stream: The stream associated with the input node (if any).
            properties: Additional properties for the input node.
            sync: Whether to synchronize the input node immediately.
        """
        input_node = self.create_node(label=label, type=str(NodeType.INPUT), properties=properties, sync=sync)

        # input value/stream
        input_node.set_data('value', value, sync=sync)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, sync=sync)

        return input_node

    def define_output(self, label=None, value=None, stream=None, properties={}, sync=None):
        """Defines an output node for the plan.

        Parameters:
            label: The label for the output node.
            value: The value for the output node.
            stream: The stream associated with the output node (if any).
            properties: Additional properties for the output node.
            sync: Whether to synchronize the output node immediately.
        """
        output_node = self.create_node(label=label, type=str(NodeType.OUTPUT), properties=properties, sync=sync)

        # output value/stream
        output_node.set_data('value', value, sync=sync)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, sync=sync)

        return output_node

    def define_agent(self, name=None, label=None, properties={}, sync=None):
        """Defines an agent entity in the plan.

        Parameters:
            name: The name of the agent.
            label: The label for the agent (if different from name).
            properties: Additional properties for the agent to pass on to execution.
            sync: Whether to synchronize the agent immediately.
        """

        # checks
        if name is None:
            raise Exception("Name is not specified")
        if label and Separator.AGENT in label:
            raise Exception("Label cannot contain: " + Separator.AGENT)

        if label is None:
            label = name

        agent = self.create_agent(label=label, properties=properties, sync=sync)

        agent.set_data("name", name)
        canonical_name = name if label == name else name + Separator.AGENT + label
        agent.set_data("canonical_name", canonical_name)

        # add canonical_name to map
        self.map(canonical_name, agent.get_id(), sync=sync)

        return agent

    def define_agent_input(self, name=None, agent=None, stream=None, properties={}, sync=None):
        """Defines an agent input node in the plan.

        Parameters:
            name: The name of the input parameter.
            agent: The agent associated with the input parameter (name, id, or canonical name).
            stream: The stream associated with the input node (if any).
            properties: Additional properties for the input node.
            sync: Whether to synchronize the input node immediately.
        """
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if agent is None:
            raise Exception("Agent is not specified")

        # get agent agent
        agent = self.get_agent(agent)

        if agent:
            agent_id = agent.get_id()
            agent_canonical_name = agent.get_data("canonical_name")
        else:
            raise Exception("Agent is not in defined")

        label = self._get_default_label(agent_canonical_name, input=name)

        # agent input node
        agent_input_node = self.create_node(label=label, type=str(NodeType.AGENT_INPUT), properties=properties, sync=sync)
        agent_input_node.set_data("name", name, sync=sync)
        agent_input_node.set_data("canonical_name", label, sync=sync)
        agent_input_node.set_data("value", None, sync=sync)

        self.set_node_entity(agent_input_node.get_id(), agent_id, sync=sync)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, sync=sync)

        return agent_input_node

    def define_agent_output(self, name, agent, properties={}, sync=None):
        """Defines an agent output node in the plan.

        Parameters:
            name: The name of the output parameter.
            agent: The agent associated with the output parameter (name, id, or canonical name).
            properties: Additional properties for the output node.
            sync: Whether to synchronize the output node immediately.
        """
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if agent is None:
            raise Exception("Agent is not specified")

        # get agent agent
        agent = self.get_agent(agent)

        if agent:
            agent_id = agent.get_id()
            agent_canonical_name = agent.get_data("canonical_name")
        else:
            raise Exception("Agent is not in defined")

        label = self._get_default_label(agent_canonical_name, output=name)

        # agent output node
        agent_output_node = self.create_node(label=label, type=str(NodeType.AGENT_OUTPUT), properties=properties, sync=sync)
        agent_output_node.set_data("name", name, sync=sync)
        agent_output_node.set_data("canonical_name", label, sync=sync)
        agent_output_node.set_data("value", None, sync=sync)

        self.set_node_entity(agent_output_node.get_id(), agent_id, sync=sync)

        return agent_output_node

    ### agent
    def create_agent(self, label=None, properties=None, sync=None):
        """Creates an agent entity in the plan.

        Parameters:
            label: The label for the agent. Defaults to None.
            properties: Additional properties for the agent. Defaults to None.
            sync: Whether to synchronize immediately. Defaults to None.

        Returns:
            The created agent entity.
        """
        return self.create_entity(label=label, type=str(EntityType.AGENT), properties=properties, sync=sync)

    def get_agents(self):
        """
        Returns a list of all agent entities in the plan.

        Returns:
            List of agent entities.
        """
        return self.get_entities(type=str(EntityType.AGENT))

    def get_agent(self, a, cls=None):
        """Retrieves an agent entity by its identifier, label, or canonical name.

        Parameters:
            a: The identifier, label, or canonical name of the agent.
            cls: Optional class type for the agent entity. Defaults to None.

        Returns:
            The agent entity if found, else None.
        """
        return self.get_entity(a, type=str(EntityType.AGENT))

    def get_agent_by_id(self, agent_id, cls=None):
        return self.get_entity_by_id(agent_id, type=str(EntityType.AGENT), cls=cls)

    def get_agent_by_label(self, agent_label, cls=None):
        return self.get_entity_by_label(agent_label, type=str(EntityType.AGENT), cls=cls)

    def get_agent_properties(self, a):
        agent = self.get_agent(a)
        if agent:
            return agent.get_properties()
        return {}

    ### stream
    def create_stream(self, label=None, properties=None, sync=None):
        return self.create_entity(label=label, type=str(EntityType.STREAM), properties=properties, sync=sync)

    def get_streams(self):
        return self.get_entities(type=str(EntityType.STREAM))

    def get_stream(self, a, cls=None):
        return self.get_entity(a, type=str(EntityType.STREAM))

    def get_stream_by_id(self, stream_id, cls=None):
        return self.get_entity_by_id(stream_id, type=str(EntityType.STREAM), cls=cls)

    def get_stream_by_label(self, stream_label, cls=None):
        return self.get_entity_by_label(stream_label, type=str(EntityType.STREAM), cls=cls)

    def get_nodes_by_stream(self, s, node_type=None):
        return self.get_nodes_by_entity(s, type=str(EntityType.STREAM), node_type=node_type)

    def count_streams(self, filter_status=None):
        count = 0
        streams = self.get_streams()
        for stream_id in streams:
            stream = self.get_stream(stream_id)
            status = stream.get_data("status")

            if filter_status:
                if status not in filter_status:
                    continue

            count = count + 1

        return count

    # node
    def get_node_value(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")

        value = node.get_data("value")

        if value is None:
            return self.fetch_node_value_from_stream(n)

    def set_node_value_from_stream(self, n, sync=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")

        node.set_data("value", self.fetch_node_value_from_stream(n), sync=sync)

    def fetch_node_value_from_stream(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")

        # get from stream
        stream = self.get_node_entity(n, type=str(EntityType.STREAM))

        stream_status = stream.get_data("status")
        if stream_status == Status.FINISHED:
            return self.get_stream_value(stream)

        return None

    def set_node_stream(self, n, stream, sync=None):
        stream_node = self.get_stream(stream)
        if stream_node is None:
            stream_node = self.create_stream(label=stream, sync=sync)
            stream_node.set_data("status", str(Status.INITED), sync=sync)
            stream_node.set_data("value", None, sync=sync)

        self.set_node_entity(n, stream, sync=sync)

    def get_node_stream(self, n):
        return self.get_node_entity(n, type=str(EntityType.STREAM))

    # status, value
    def set_stream_status(self, s, status, sync=None):
        stream = self.get_stream(s)
        if stream:
            stream.set_data("status", str(status), sync=sync)

    def get_stream_status(self, s):
        stream = self.get_stream(s)
        if stream:
            return stream.get_data("status")
        return None

    def set_stream_value(self, s, value, sync=None):
        stream = self.get_stream(s)
        if stream:
            stream.set_data("value", value, sync=sync)

    def append_stream_value(self, s, value, sync=None):
        stream = self.get_stream(s)
        if stream:
            stream.append_data("value", value, sync=sync)

    def get_stream_value(self, s):
        stream = self.get_stream(s)
        if stream:
            return stream.get_data("value")
        return None

    # discovery
    def match_stream(self, stream):
        node = None
        stream_prefix = self.get_scope() + ":" + "PLAN" + ":" + self.get_id()
        # TODO: REVISE THIS LOGIC!
        if stream.find(stream_prefix) == 0:
            s = stream[len(stream_prefix) + 1 :]
            ss = s.split(":")

            agent = ss[0]
            param = ss[3]

            default_label = self._get_default_label(agent, output=param)

            node = self.get_node(default_label)

        return node

    # node functions
    def set_node_value(self, n, value, sync=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be set")

        node.set_data("value", value, sync=sync)

    def get_node_properties(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be get")

        return node.get_properties()

    def get_node_property(self, n, property):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be get")

        return node.get_property(property)

    def set_node_properties(self, n, properties, sync=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")

        for property in properties:
            node.set_property(property, properties[property], sync=sync)

    def set_node_property(self, n, property, value, sync=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")

        node.set_property(property, value, sync=sync)

    def get_node_type(self, n):
        node = self.get_node(n)

        if node is None:
            raise Exception("Type for non-existing node cannot be get")

        return node.get_type()

    def get_node_agent(self, n):
        return self.get_node_entity(n, type=str(EntityType.AGENT))

    ## connections
    def _resolve_input_output_node_id(self, input=None, output=None, sync=None):
        n = None
        if input:
            n = input
        elif output:
            n = output
        else:
            raise Exception("Input/Output should be specified")

        node = self.get_node(n)

        if node is None:
            # create node
            if input:
                node = self.define_input(label=input, sync=sync)
            elif output:
                node = self.define_output(label=output, sync=sync)

        return node.get_id()

    def _resolve_agent_param_node_id(self, agent=None, agent_param=None, node_type=None, sync=None):
        node_id = None
        if agent:
            if agent_param is None:
                agent_param = "DEFAULT"

            agent_node = self.get_agent(agent)
            if agent_node is None:
                agent_node = self.define_agent(name=agent, sync=sync)

            agent_canonical_name = agent_node.get_data("canonical_name")
            label = None
            if node_type == NodeType.AGENT_INPUT:
                label = self._get_default_label(agent_canonical_name, input=agent_param)
            elif node_type == NodeType.AGENT_OUTPUT:
                label = self._get_default_label(agent_canonical_name, output=agent_param)

            agent_param_node = self.get_node(label)
            if agent_param_node is None:
                if node_type == NodeType.AGENT_INPUT:
                    agent_param_node = self.define_agent_input(name=agent_param, agent=agent, sync=sync)
                elif node_type == NodeType.AGENT_OUTPUT:
                    agent_param_node = self.define_agent_output(name=agent_param, agent=agent, sync=sync)

            node_id = agent_param_node.get_id()

        elif agent_param:
            agent_param_node = self.get_node(agent_param)
            node_id = agent_param_node.get_id()
        else:
            raise Exception("Non-existing agent input/output cannot be connected")

        return node_id

    def connect_input_to_agent(self, from_input=None, to_agent=None, to_agent_input=None, sync=None):

        from_id = self._resolve_input_output_node_id(input=from_input, sync=sync)
        to_id = self._resolve_agent_param_node_id(agent=to_agent, agent_param=to_agent_input, node_type=NodeType.AGENT_INPUT, sync=sync)
        self.connect_nodes(from_id, to_id, sync=sync)

    def connect_agent_to_agent(self, from_agent=None, from_agent_output=None, to_agent=None, to_agent_input=None, sync=None):

        from_id = self._resolve_agent_param_node_id(agent=from_agent, agent_param=from_agent_output, node_type=NodeType.AGENT_OUTPUT, sync=sync)
        to_id = self._resolve_agent_param_node_id(agent=to_agent, agent_param=to_agent_input, node_type=NodeType.AGENT_INPUT, sync=sync)
        self.connect_nodes(from_id, to_id, sync=sync)

    def connect_agent_to_output(self, from_agent=None, from_agent_output=None, to_output=None, sync=None):

        from_id = self._resolve_agent_param_node_id(agent=from_agent, agent_param=from_agent_output, node_type=NodeType.AGENT_OUTPUT, sync=sync)
        to_id = self._resolve_input_output_node_id(output=to_output, sync=sync)
        self.connect_nodes(from_id, to_id, sync=sync)

    def connect_input_to_output(self, from_input=None, to_output=None, sync=None):

        from_id = self._resolve_input_output_node_id(input=from_input, sync=sync)
        to_id = self._resolve_input_output_node_id(output=to_output, sync=sync)
        self.connect_nodes(from_id, to_id, sync=sync)

    # plan execution i/o
    def _write_to_stream(self, worker, data, output, tags=None, eos=True):
        # tags
        if tags is None:
            tags = []
        # auto-add HIDDEN
        tags.append("HIDDEN")

        # data
        output_stream = worker.write_data(data, output=output, id=self.get_id(), tags=tags, scope="worker")

        # eos
        if eos:
            worker.write_eos(output=output, id=self.get_id(), scope="worker")

        return output_stream

    def _write_data(self, worker, data, output, eos=True):
        return self._write_to_stream(worker, data, output, eos=eos)

    def _write_plan(self, worker, eos=True):
        return self._write_to_stream(worker, self.get_data(), "PLAN", tags=["PLAN"], eos=eos)

    # plan execution status/checks
    def _detect_leaves(self):
        self.leaves = []

        nodes = self.get_nodes()
        for node_id in nodes:
            if self.is_node_leaf(node_id):
                self.leaves.append(node_id)

    def check_status(self, sync=None):
        if self.leaves is None:
            self._detect_leaves()

        status = Status.FINISHED

        for leaf_id in self.leaves:
            leaf_stream = self.get_node_stream(leaf_id)
            if leaf_stream is None:
                status = Status.RUNNING
                break
            leaf_stream_status = self.get_stream_status(leaf_stream)
            if leaf_stream_status != Status.FINISHED:
                status = Status.RUNNING
                break

        self.set_status(status, sync=sync)
        return status

    # plan submit
    def submit(self, worker, sync=None):
        # process inputs with initialized values, if any
        nodes = self.get_nodes()
        for node_id in nodes:
            node = self.get_node(node_id)

            # inputs
            if node.get_type() == NodeType.INPUT:
                node_value = node.get_data("value")
                if node_value:
                    node_label = node.get_label()
                    # write data for input
                    stream = self._write_data(worker, node_value, node_label)
                    # set stream for node
                    self.set_node_stream(node_id, stream, sync=sync)
            # outputs
            if node.get_type() == NodeType.OUTPUT:
                node_value = node.get_data("value")
                if node_value:
                    node_label = node.get_label()
                    # write data for output
                    stream = self._write_data(worker, node_value, node_label)
                    # set stream for node
                    self.set_node_stream(node_id, stream, sync=sync)

        # set status
        self.set_status(Status.SUBMITTED, sync=sync)

        # write plan
        self._write_plan(worker)

    @classmethod
    def _validate(cls, d):
        dv = super(AgenticPlan, cls)._validate(d)
        if dv is None:
            return None
        if 'context' not in dv:
            return None
        else:
            context = dv['context']
            if 'scope' not in context:
                return None

        return dv
