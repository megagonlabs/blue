###### Parsers, Utils
import json
import logging

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.agent import Agent
from blue.session import Session
from blue.stream import Constant, ControlCode, ConstantEncoder
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, json_utils, dag_utils


###############
### Status
class Status(Constant):
    def __init__(self, c):
        super().__init__(c)


Status.INACTIVE = Status("INACTIVE")
Status.SUBMITTED = Status("SUBMITTED")
Status.INITED = Status("INITED")
Status.PLANNED = Status("PLANNED")
Status.RUNNING = Status("RUNNING")
Status.FINISHED = Status("FINISHED")


class NodeType(Constant):
    def __init__(self, c):
        super().__init__(c)


NodeType.INPUT = Constant("INPUT")
NodeType.OUTPUT = Constant("OUTPUT")
NodeType.AGENT_INPUT = Constant("AGENT_INPUT")
NodeType.AGENT_OUTPUT = Constant("AGENT_OUTPUT")


class EntityType(Constant):
    def __init__(self, c):
        super().__init__(c)


EntityType.AGENT = Constant("AGENT")
EntityType.STREAM = Constant("STREAM")


##############
### Plan
#
class Plan(dag_utils.DAG):

    def __init__(self, scope=None, id=None, label=None, type="PLAN", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        self.leaves = None
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

        s = scope
        if isinstance(s, Session):
            s = scope.cid

        self._set_scope(s, sync=sync)

    def _init_data(self, sync=None):
        super()._init_data(sync=sync)

        self.set_data("context", {"scope": None}, sync=sync)
        self.set_status(Status.INACTIVE, sync=sync)
        self.set_data("agents", {}, sync=sync)
        self.set_data("streams", {}, sync=sync)

    # properties
    def _initialize_properties(self, sync=None):
        super()._initialize_properties(sync=sync)

        # db connectivity
        self.set_property('db.host', 'localhost', sync=sync)
        self.set_property('db.port', 6379, sync=sync)

    # context, scope
    def get_context(self):
        return self.get_data("context")

    def get_scope(self):
        context = self.get_context()
        if 'scope' in context:
            return context['scope']
        else:
            return None

    def _set_scope(self, scope, sync=None):
        context = self.get_context()
        context['scope'] = scope

        self.synchronize(key="context.scope", value=scope)

    # status
    def set_status(self, status, sync=None):
        self.set_data("status", str(status), sync=sync)

    def get_status(self):
        return self.get_data('status')

    #### plan specific nodes, agents
    # inputs, outputs, agents, w/input and output parameters
    def _get_default_label(self, agent, input=None, output=None):
        label = agent

        if input:
            label = label + ".INPUT:" + input
        elif output:
            label = label + ".OUTPUT:" + output

        return label

    def define_input(self, label=None, value=None, stream=None, properties={}, sync=None):
        if label is None:
            raise Exception("Label is not specified")
        input_node = self.create_node(label=label, type=str(NodeType.INPUT), properties=properties, sync=sync)

        # input value/stream
        input_node.set_data('value', value, sync=sync)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, sync=sync)

        return input_node

    def define_output(self, label=None, value=None, stream=None, properties={}, sync=None):
        if label is None:
            raise Exception("Label is not specified")
        output_node = self.create_node(label=label, type=str(NodeType.OUTPUT), properties=properties, sync=sync)

        # output value/stream
        output_node.set_data('value', value, sync=sync)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, sync=sync)

        return output_node

    def define_agent(self, name=None, label=None, properties={}, sync=None):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if label and Agent.SEPARATOR in label:
            raise Exception("Label cannot contain: " + Agent.SEPARATOR)

        if label is None:
            label = name
        agent = self.create_agent(label=label, properties=properties, sync=sync)

        agent.set_data("name", name)
        canonical_name = name if label == name else name + Agent.SEPARATOR + label
        agent.set_data("canonical_name", canonical_name)
        agent.set_data('children', [])

        # add canonical_name to map
        self.map(canonical_name, agent.get_id(), sync=sync)

        return agent

    def define_agent_input(self, name=None, agent=None, stream=None, properties={}, sync=None):
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
        agent_input_node.set_data("stream", None, sync=sync)
        agent_input_node.set_data("parent", agent_id, sync=sync)

        # agent
        agent.append_data('children', agent_input_node.get_id(), sync=sync)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, sync=sync)

        return agent_input_node

    def define_agent_output(self, name, agent, properties={}, sync=None):
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
        agent_output_node.set_data("stream", None, sync=sync)
        agent_output_node.set_data("parent", agent_id, sync=sync)

        # agent
        agent.append_data('children', agent_output_node.get_id(), sync=sync)

        return agent_output_node

    ### agent
    def _verify_agent(self, label=None, properties=None):
        # verify if label is unique
        if label and self.is_mapped(label):
            return False

        return True

    def create_agent(self, label=None, properties=None, sync=None):
        # verify agent, first
        if not self._verify_agent(label=label, properties=properties):
            raise Exception("Cannot create agent due to failed varification")

        # create agent entity
        agent = dag_utils.Entity(
            label=label, type=str(EntityType.AGENT), properties=properties, path=self.path + "." + self.get_id() + ".agents", synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=sync
        )
        agent_id = agent.get_id()
        agent_label = agent.get_label()

        # add to agents
        agents = self.get_agents()
        agents[agent_id] = agent.get_data()

        # add to map
        if label:
            self.map(agent_label, agent_id, sync=sync)

        return agent

    def get_agents(self):
        return self.get_data("agents")

    def get_agent(self, a, cls=None):
        agent = self.get_agent_by_id(a, cls=cls)
        if agent is None:
            agent = self.get_agent_by_label(a, cls=cls)
        return agent

    def get_agent_by_id(self, agent_id, cls=None):
        agents = self.get_agents()
        if agent_id in agents:
            agent_data = agents[agent_id]
            if cls is None:
                cls = dag_utils.Entity
            return cls.from_dict(agent_data, path=self.path + "." + self.get_id() + ".agents", synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=False)
        else:
            return None

    def get_agent_by_label(self, agent_label, cls=None):
        map = self.get_data("map")
        agent = None
        if agent_label in map:
            agent_id = map[agent_label]
            agent = self.get_agent_by_id(agent_id)
        return agent

    def get_agent_properties(self, a):
        agent = self.get_agent(a)
        if agent:
            return agent.get_properties()
        return {}

    ### stream
    def _verify_stream(self, label=None, type=None, properties=None):
        # verify if label is unique
        if label and self.is_mapped(label):
            return False

        return True

    def create_stream(self, label=None, properties=None, sync=None):
        # verify stream, first
        if not self._verify_stream(label=label, type=type, properties=properties):
            raise Exception("Cannot create stream due to failed varification")

        # create stream
        stream = dag_utils.Entity(
            label=label,
            type=str(EntityType.STREAM),
            properties=properties,
            path=self.path + "." + self.get_id() + ".streams",
            synchronizer=self.synchronizer,
            auto_sync=self.auto_sync,
            sync=sync,
        )
        stream_id = stream.get_id()
        stream_label = stream.get_label()

        # add to streams
        streams = self.get_streams()
        streams[stream_id] = stream.get_data()

        # add to map
        if label:
            self.map(stream_label, stream_id, sync=sync)

        return stream

    def get_streams(self):
        return self.get_data("streams")

    def get_stream(self, a, cls=None):
        stream = self.get_stream_by_id(a, cls=cls)
        if stream is None:
            stream = self.get_stream_by_label(a, cls=cls)
        return stream

    def get_stream_by_id(self, stream_id, cls=None):
        streams = self.get_streams()
        if stream_id in streams:
            stream_data = streams[stream_id]
            if cls is None:
                cls = dag_utils.Entity
            return cls.from_dict(stream_data, path=self.path + "." + self.get_id() + ".streams", synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=False)
        else:
            return None

    def get_stream_by_label(self, stream_label, cls=None):
        map = self.get_data("map")
        stream = None
        if stream_label in map:
            stream_id = map[stream_label]
            stream = self.get_stream_by_id(stream_id)
        return stream

    def get_nodes_by_stream(self, s, node_type=None):
        stream = self.get_stream(s)
        if stream is None:
            return []
        nodes = []

        ids = stream.get_data("nodes")
        for id in ids:
            node = self.get_node(id)
            if node_type:
                if type(node_type) == list:
                    if node.get_type() in node_type:
                        nodes.append(node)
                else:
                    if node.get_type() == node_type:
                        nodes.append(node)
            else:
                nodes.append(node)
        return nodes

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
        stream_id = node.get_data("stream")
        stream = self.get_stream(stream_id)
        stream_status = stream.get_data("status")
        if stream_status == Status.FINISHED:
            return self.get_stream_value(stream)

        return None

    def set_node_stream(self, n, stream, sync=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Stream for non-existing node cannot be set")

        node_id = node.get_id()

        if stream is None:
            node.set_data("stream", None, sync=sync)
        else:
            stream_node = self.get_stream(stream)
            if stream_node is None:
                stream_node = self.create_stream(label=stream, sync=sync)
                stream_node.set_data("nodes", [], sync=sync)
                stream_node.set_data("status", str(Status.INITED), sync=sync)
                stream_node.set_data("value", None, sync=sync)

            stream_node.append_data("nodes", node_id, sync=sync)
            node.set_data("stream", stream_node.get_id(), sync=sync)

    def get_node_stream(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Stream for non-existing node cannot be get")

        return node.get_data("stream")

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

    def get_parent_node(self, n):
        node = self.get_node(n)

        parent_id = node.get_data("parent")
        parent_node = self.get_agent(parent_id)

        return parent_node

    def get_prev_nodes(self, n):
        node = self.get_node(n)
        prev_nodes = []
        if node:
            prev_ids = node.get_data('prev')
            for prev_id in prev_ids:
                prev_node = self.get_node_by_id(prev_id)
                if prev_node:
                    prev_nodes.append(prev_node)

        return prev_nodes

    def get_next_nodes(self, n):
        node = self.get_node(n)
        next_nodes = []
        if node:
            next_ids = node.get_data('next')
            for next_id in next_ids:
                next_node = self.get_node_by_id(next_id)
                if next_node:
                    next_nodes.append(next_node)

        return next_nodes

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
            leaf_node = self.get_node(leaf_id)
            leaf_stream = leaf_node.get_data("stream")
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
        dv = super(Plan, cls)._validate(d)
        if dv is None:
            return None
        if 'context' not in dv:
            return None
        else:
            context = dv['context']
            if 'scope' not in context:
                return None
        if 'agents' not in dv:
            dv['agents'] = {}
        if 'streams' not in dv:
            dv['streams'] = {}

        return dv
