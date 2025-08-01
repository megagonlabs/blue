###### Parsers, Utils
import json
import logging
import copy

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.session import Session
from blue.stream import Constant, ControlCode, ConstantEncoder
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, json_utils


class Base:
    def __init__(self, name, id=None, label=None, type=None, path=None, properties=None, synchronizer=None, auto_sync=False):

        # name
        self.name = name

        # id
        if id:
            self.id = id
        else:
            self.id = uuid_utils.create_uuid()

        # label
        if label is None:
            label = name

        # type
        self.type = type

        # sync path
        if path is None:
            path = "$"
        self.auto_sync = auto_sync
        if synchronizer:
            self.synchronizer = synchronizer

        self._initialize(properties=properties)

    def _initialize(self, properties=None):
        self.properties = {}

        self._initialize_properties()
        self._update_properties(properties=properties)

    # override
    def _initialize_properties(self):
        return

    def _update_properties(self, properties=None, sync=False):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

        if self.auto_sync or sync:
            self.synchronizer(path=self.path + ".properties")

    # attributes
    def set_attribute(self, key, value, sync=False):
        setattr(self, key, value)

        if self.auto_sync or sync:
            self.synchronizer(path=self.path + "." + key)

    def get_attribute(self, key):
        if key in self.__dict__:
            return getattr(self, key)
        return None

    def get_attributes(self):
        return self.__dict__

    # properties
    def set_property(self, key, value, sync=False):
        self.properties[key] = value

        if self.auto_sync or sync:
            self.synchronizer(path=self.path + ".properties." + key)

    def get_property(self, key):
        if key in self.properties:
            return self.properties[key]
        return None

    def get_properties(self):
        return self.properties

    def toJSON(self):
        base = {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "type": self.type,
        }
        # add attributes
        base = json_utils.merge_json(base, copy.deepcopy(self.get_attributes()))
        # add properties
        base = json_utils.merge_json(base, {"properties": copy.deepcopy(self.get_properties())})
        return base


class Node(Base):
    def __init__(self, name, id=None, label=None, path=None, properties=None):
        super().__init__(name, id=id, label=label, path=path, properties=properties)

        self.prev = []
        self.next = []


class DAG:
    def __init__(self, label=None, type=None, prefix=None, properties=None, data=None):

        # id
        id = uuid_utils.create_uuid()

        # type
        if type is None:
            type = "DAG"

        sid = type + ":" + id

        cid = sid
        if prefix:
            cid = prefix + ":" + sid

        # reprensentation
        self._repr = {"id": id, "sid": sid, "cid": cid, "label": label, "type": type, "properties": {}, "data": {}, "nodes": {}, "map": {}}

        if properties == None:
            properties = {}
        self._initialize(properties=properties)

        # start
        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self._repr['properties'] = {}

        # db connectivity
        self._repr['properties']['db.host'] = 'localhost'
        self._repr['properties']['db.port'] = 6379

    def _update_properties(self, properties=None, save=False):
        if properties is None:
            return

        # override
        for p in properties:
            self._repr['properties'][p] = properties[p]

        if save:
            self.save(path="$.properties")

    ###### DAG
    @classmethod
    def _verify_repr(cls, repr):
        if type(repr) == dict:
            if 'id' not in repr:
                return None
            if 'cid' not in repr:
                return None
            if 'label' not in repr:
                return None
            if 'type' not in repr:
                return None
            if 'properties' not in repr:
                return None
            if 'data' not in repr:
                return None
            if 'nodes' not in repr:
                return None
            if 'map' not in repr:
                return None
        else:
            return None
        return repr

    # build a declaratively, from a json spec
    @classmethod
    def from_json(cls, repr, save=False):
        if type(repr) == str:
            try:
                repr = json.loads(repr)
            except:
                repr = None

        # verify repr
        repr = Plan._verify_repr(repr)

        if repr:

            id = repr['id']
            cid = repr['cid']
            scid = cid.split(":")
            # extract type, prefix
            type = scid[-2]
            prefix = ":".join(scid[:-2])
            label = repr['label']

            properties = repr['properties']
            data = repr['data']

            # create instance
            dag = cls(label=label, type=type, id=id, prefix=prefix, properties=properties, data=data)

            # set repr
            dag._repr = repr

            if save:
                dag.save()

            # return
            return dag
        else:
            raise Exception("Invalid dag repr")

    def to_json(self):
        return json.dumps(self._repr)

    def get_nodes(self):
        return self._repr['nodes']

    def count_nodes(self, filter_node_type=None, filter_hasPrev=None, filter_hasNext=None):
        count = 0
        nodes = self.get_nodes()
        for node_id in nodes:
            node = self.get_node_by_id(node_id)
            node_type = node['type']
            prev = node['prev']
            next = node['next']

            if filter_node_type:
                if node_type not in filter_node_type:
                    continue

            if filter_hasPrev:
                if len(prev) == 0:
                    continue

            if filter_hasNext:
                if len(next) == 0:
                    continue

            count = count + 1

        return count

    def detect_leaves(self):
        self.leaves = []

        nodes = self.get_nodes()
        for node_id in nodes:
            if self.is_node_leaf(node_id):
                self.leaves.append(node_id)

    ## properties
    def get_properties(self):
        return self._repr['properties']

    def get_property(self, key):
        if key in self._repr['properties']:
            return self._repr['properties'][key]
        else:
            return None

    def set_property(self, key, value, save=False):
        self._repr['properties'][key] = value

        if save:
            self.save(path="$.properties['" + key + "']")

    ## data
    def get_data(self, key):
        if key in self._repr['data']:
            return self._repr['data'][key]
        else:
            return None

    def set_data(self, key, value, save=False):
        self._repr['data'][key] = value

        if save:
            self.save(path="$.data['" + key + "']")

    ###### NODE
    def create_node(self, label=None, type=None, properties=None, data=None, save=False):

        # verify unique label
        if label and label in self._repr['map']:
            raise Exception("label should be unique")

        # id
        id = uuid_utils.create_uuid()

        # type
        if type is None:
            type = "NODE"

        sid = type + ":" + id

        cid = sid

        # use graph.cid as prefix
        prefix = self.cid
        cid = prefix + ":" + sid

        # reprensentation
        if properties is None:
            properties = {}
        if data is None:
            data = {}

        node = {"id": id, "sid": sid, "cid": cid, "label": label, "type": type, "properties": properties, "data": data, "prev": {}, "next": {}}

        # add to dag representation
        self._repr['nodes'][id] = node
        if label:
            self._repr['map'][label] = id

        # persis
        if save:
            self.save(path="$.nodes[']" + id + "']")
            if label:
                self.save(path="$.map['" + label + "']")

        return node

    def delete_node(self, n, save=False):
        node = self.get_node(n)
        id = node['id']

        # delete from prev_nodes
        prev_nodes = self.get_prev_nodes(n)
        for prev_node in prev_nodes:
            prev_node_id = prev_node['id']
            del prev_node["next"][id]

            if save:
                self.save(path="$.nodes[']" + prev_node_id + "']")

        # delete from next_nodes
        next_nodes = self.get_next_nodes(n)
        for next_node in next_nodes:
            next_node_id = next_node['id']
            del next_nodes["prev"][id]

            if save:
                self.save(path="$.nodes[']" + next_node_id + "']")

        # delete from nodes
        del self._repr['nodes'][id]

        if save:
            self.save(path="$.nodes[']" + id + "']")

    def get_node_by_id(self, id):
        if id in self._repr['nodes']:
            return self._repr['nodes'][id]

    def get_node_by_label(self, label):
        if label in self._repr['map']:
            id = self._repr['map'][label]
            return self.get_node_by_id(id)

    def get_node(self, n):
        node = None
        if n in self._repr['nodes']:
            node = self.get_node_by_id(n)
        else:
            node = self.get_node_by_label(n)
        return node

    def get_node_type(self, n):
        node = self.get_node(n)

        return node['type']

    def get_node_id(self, n):
        node = self.get_node(n)

        return node['id']

    def get_node_label(self, n):
        node = self.get_node(n)

        return node['label']

    def get_prev_nodes(self, n):
        node = self.get_node(n)
        prev_nodes = []
        if node:
            prev_ids = node['prev']
            for prev_id in prev_ids:
                prev_node = self.get_node_by_id(prev_id)
                if prev_node:
                    prev_nodes.append(prev_node)

        return prev_nodes

    def get_next_nodes(self, n):
        node = self.get_node(n)
        next_nodes = []
        if node:
            next_ids = node['next']
            for next_id in next_ids:
                next_node = self.get_node_by_id(next_id)
                if next_node:
                    next_nodes.append(next_node)

        return next_nodes

    def is_node_leaf(self, n):
        node = self.get_node(n)
        prev = node['prev']
        next = node['next']

        if len(prev) > 0 and len(next) == 0:
            return True
        else:
            return False

    ## properties
    def get_node_properties(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be get")

        return node['properties']

    def get_node_property(self, n, key):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be get")

        properties = node['properties']
        if key in properties:
            return properties[key]
        else:
            return None

    def set_node_properties(self, n, properties, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")

        node['properties'] = properties

        if save:
            self.save(path="$.nodes['" + id + "'].properties")

    def set_node_property(self, n, key, value, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")

        properties = node['properties']
        properties[key] = value

        if save:
            self.save(path="$.nodes['" + id + "'].properties['" + key + "']")

    ## data
    def get_node_data(self, n, key):
        node = self.get_node(n)
        if node is None:
            raise Exception("Data for non-existing node cannot be get")

        data = node['data']
        if key in data:
            return data[key]
        else:
            return None

    def set_node_data(self, n, key, value, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Data for non-existing node cannot be set")

        data = node['data']
        data[key] = value

        if save:
            self.save(path="$.nodes['" + id + "'].data['" + key + "']")

    ### LINKS
    def create_link(self, from_node, to_node, save=False):
        pass

    #### CONNECTION, PERSISTENCE
    # persistence
    def _get_dag_data_namespace(self):
        return self.cid + ":DATA"

    def _safe_json(self, o):
        if type(o) == dict:
            s = json.dumps(o, cls=ConstantEncoder)
            return json.loads(s)
        elif isinstance(o, Constant):
            return str(o)
        else:
            return o

    def save(self, path=None):
        if path is None:
            path = "$"

        data = json_utils.json_query(self._repr, path, single=True)

        safe_data = self._safe_json(data)

        self.connection.json().set(self._get_plan_data_namespace(), path, safe_data)

    def _start(self):
        self._start_connection()

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()


###############
### Plan
#
class Plan(DAG):
    def __init__(self, id=None, scope=None, properties=None):
        super().__init__("PLAN", id=id, prefix=scope, properties=properties)

    #### CONNECTION
    def _start(self):
        super()._start()

        self.leaves = None

    #### PLAN

    def define_input(self, name, label=None, value=None, stream=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._repr['map']:
            raise Exception("Name should be unique")
        if label and label in self._repr['map']:
            raise Exception("Labels should be unique")

        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        if label is None:
            label = name
        node['label'] = label
        node['type'] = NodeType.INPUT
        node['value'] = value
        node['stream'] = stream
        node['properties'] = properties
        node['parent'] = None
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # add to plan
        self._repr['nodes'][id] = node
        self._repr['map'][label] = id
        self._repr['map'][name] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.map['" + label + "']")
            self.save(path="$.map['" + name + "']")

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

        return node

    def define_output(self, name, label=None, value=None, stream=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._repr['map']:
            raise Exception("Name should be unique")
        if label and label in self._repr['map']:
            raise Exception("Labels should be unique")

        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        if label is None:
            label = name
        node['label'] = label
        node['type'] = NodeType.OUTPUT
        node['value'] = value
        node['stream'] = stream
        node['properties'] = properties
        node['parent'] = None
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # add to plan
        self._repr['nodes'][id] = node
        self._repr['map'][label] = id
        self._repr['map'][name] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.map['" + label + "']")
            self.save(path="$.map['" + name + "']")

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

        return node

    def define_agent(self, name, label=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._repr['map']:
            raise Exception("Name should be unique")
        if label and label in self._repr['map']:
            raise Exception("Labels should be unique")

        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        if label is None:
            label = name
        node['label'] = label
        node['type'] = NodeType.AGENT
        node['value'] = None
        node['stream'] = None
        node['properties'] = properties
        node['parent'] = None
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # add to plan
        self._repr['nodes'][id] = node
        self._repr['map'][label] = id
        self._repr['map'][name] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.map['" + label + "']")
            self.save(path="$.map['" + name + "']")

        return node

    def define_agent_input(self, name, agent, label=None, stream=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if agent is None:
            raise Exception("Agent is not specified")
        if label and label in self._repr['map']:
            raise Exception("Labels should be unique")

        # get agent name
        agent_id = None
        agent_name = None
        agent_node = self.get_node(agent)
        if agent_node:
            agent_id = agent_node['id']
            agent_name = agent_node['name']
        if agent_id is None:
            raise Exception("Agent is not in defined")

        default_label = self._get_default_label(agent_name, input=name)
        if label is None:
            label = default_label

        if default_label and default_label in self._repr['map']:
            raise Exception("Labels should be unique")

        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        node['label'] = label
        node['type'] = NodeType.AGENT_INPUT
        node['value'] = None
        node['stream'] = None
        node['properties'] = properties
        node['parent'] = agent_id
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # agent attributes
        agent_node['children'].append(id)

        # add to plan
        self._repr['nodes'][id] = node
        self._repr['map'][label] = id
        self._repr['map'][default_label] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.map['" + label + "']")
            self.save(path="$.map['" + default_label + "']")
            self.save(path="$.nodes['" + agent_id + "'].children")

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

        return node

    def define_agent_output(self, name, agent, label=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if agent is None:
            raise Exception("Agent is not specified")
        if label and label in self._repr['map']:
            raise Exception("Labels should be unique")

        # get agent name
        agent_id = None
        agent_name = None
        agent_node = self.get_node(agent)
        if agent_node:
            agent_id = agent_node['id']
            agent_name = agent_node['name']
        if agent_id is None:
            raise Exception("Agent is not in defined")

        default_label = self._get_default_label(agent_name, output=name)
        if label is None:
            label = default_label

        if default_label and default_label in self._repr['map']:
            raise Exception("Labels should be unique")

        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        node['label'] = label
        node['type'] = NodeType.AGENT_OUTPUT
        node['value'] = None
        node['stream'] = None
        node['properties'] = properties
        node['parent'] = agent_id
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # agent attributes
        agent_node['children'].append(id)

        # add to plan
        self._repr['nodes'][id] = node
        self._repr['map'][label] = id
        self._repr['map'][default_label] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.map['" + label + "']")
            self.save(path="$.map['" + default_label + "']")
            self.save(path="$.nodes['" + agent_id + "'].children")

        return node

    # node functions

    def get_streams(self):
        return self._repr['streams']

    def count_streams(self, filter_status=None):
        count = 0
        streams = self.get_streams()
        for stream_id in streams:
            stream = streams[stream_id]
            status = stream['status']

            if filter_status:
                if status not in filter_status:
                    continue

            count = count + 1

        return count

    def get_node_value(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")

        value = node['value']

        if value is None:
            return self.fetch_node_value_from_stream(n)

    def set_node_value_from_stream(self, n, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")

        node['value'] = self.fetch_node_value_from_stream(n)

        if save:
            id = node['id']
            self.save(path="$.nodes['" + id + "'].value")

    def fetch_node_value_from_stream(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")

        # get from stream
        stream = node['stream']
        stream_status = self.get_stream_status(stream)
        if stream_status == Status.FINISHED:
            return self.get_stream_value(stream)

        return None

    def set_node_value(self, n, value, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be set")

        node['value'] = value

        if save:
            id = node['id']
            self.save(path="$.nodes['" + id + "'].value")

    def set_node_stream(self, n, stream, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Stream for non-existing node cannot be set")

        node['stream'] = stream
        id = node['id']

        if stream in self._repr['streams']:
            # add node
            self._repr['streams'][stream]['nodes'].append(id)
        else:
            self._repr['streams'][stream] = {"nodes": [id], "status": Status.INITED, "value": None}

        if save:
            self.save(path="$.nodes['" + id + "'].stream")
            self.save(path="$.streams['" + stream + "']")

    def get_node_stream(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Stream for non-existing node cannot be get")

        return node['stream']

    def get_parent_node(self, n):
        node = self.get_node(n)

        parent_id = node['parent']
        parent_node = self.get_node_by_id(parent_id)

        return parent_node

    # stream functions
    def set_stream_status(self, stream, status, save=False):
        if stream in self._repr['streams']:
            self._repr['streams'][stream]['status'] = status

            if save:
                self.save(path="$.streams['" + stream + "'].status")

    def get_stream_status(self, stream):
        if stream in self._repr['streams']:
            return self._repr['streams'][stream]['status']
        else:
            return None

    def set_stream_value(self, stream, value, save=False):
        if stream in self._repr['streams']:
            self._repr['streams'][stream]['value'] = value

            if save:
                self.save(path="$.streams['" + stream + "'].value")

    def append_stream_value(self, stream, value, save=False):
        if stream in self._repr['streams']:
            va = self._repr['streams'][stream]['value']
            if va is None:
                va = []
                self._repr['streams'][stream]['value'] = va

            va.append(value)

            if save:
                self.save(path="$.streams['" + stream + "'].value")

    def get_stream_value(self, stream):
        if stream in self._repr['streams']:
            return self._repr['streams'][stream]['value']
        else:
            return None

    # stream discovery
    def match_stream(self, stream):
        node = None
        stream_prefix = self.get_scope() + ":" + self.sid
        if stream.find(stream_prefix) == 0:
            s = stream[len(stream_prefix) + 1 :]
            ss = s.split(":")

            agent = ss[0]
            param = ss[3]

            default_label = self._get_default_label(agent, output=param)

            node = self.get_node(default_label)

        return node

    ## connections
    def _connect(self, f, t, save=False):
        from_node = self.get_node(f)
        to_node = self.get_node(t)

        if from_node is None:
            raise Exception("Non-existing node cannot be connected")
        if to_node is None:
            raise Exception("Non-existing node cannot be connected")

        from_id = from_node['id']
        to_id = to_node['id']

        from_node['next'].append(to_id)
        to_node['prev'].append(from_id)

        if save:
            self.save(path="$.nodes['" + from_id + "'].next")
            self.save(path="$.nodes['" + to_id + "'].prev")

    def _resolve_input_output_node_id(self, input=None, output=None):
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
                node = self.define_input(input)
            elif output:
                node = self.define_output(output)

        return node['id']

    def _resolve_agent_param_node_id(self, agent=None, agent_param=None, node_type=None):
        node_id = None
        if agent:
            if agent_param is None:
                agent_param = "DEFAULT"

            agent_node = self.get_node(agent)
            if agent_node is None:
                agent_node = self.define_agent(agent)

            agent_name = agent_node['name']
            label = None
            if node_type == NodeType.AGENT_INPUT:
                label = self._get_default_label(agent_name, input=agent_param)
            elif node_type == NodeType.AGENT_OUTPUT:
                label = self._get_default_label(agent_name, output=agent_param)
            agent_param_node = self.get_node(label)
            if agent_param_node is None:
                if node_type == NodeType.AGENT_INPUT:
                    agent_param_node = self.define_agent_input(agent_param, agent)
                elif node_type == NodeType.AGENT_OUTPUT:
                    agent_param_node = self.define_agent_output(agent_param, agent)

            node_id = agent_param_node['id']

        elif agent_param:
            agent_param_node = self.get_node(agent_param)
            node_id = agent_param_node['id']
        else:
            raise Exception("Non-existing agent input/output cannot be connected")

        return node_id

    def connect_input_to_agent(self, from_input=None, to_agent=None, to_agent_input=None, save=False):

        from_id = self._resolve_input_output_node_id(input=from_input)
        to_id = self._resolve_agent_param_node_id(agent=to_agent, agent_param=to_agent_input, node_type=NodeType.AGENT_INPUT)
        self._connect(from_id, to_id, save=save)

    def connect_agent_to_agent(self, from_agent=None, from_agent_output=None, to_agent=None, to_agent_input=None, save=False):

        from_id = self._resolve_agent_param_node_id(agent=from_agent, agent_param=from_agent_output, node_type=NodeType.AGENT_OUTPUT)
        to_id = self._resolve_agent_param_node_id(agent=to_agent, agent_param=to_agent_input, node_type=NodeType.AGENT_INPUT)
        self._connect(from_id, to_id, save=save)

    def connect_agent_to_output(self, from_agent=None, from_agent_output=None, to_output=None, save=False):

        from_id = self._resolve_agent_param_node_id(agent=from_agent, agent_param=from_agent_output, node_type=NodeType.AGENT_OUTPUT)
        to_id = self._resolve_input_output_node_id(output=to_output)
        self._connect(from_id, to_id, save=save)

    def connect_input_to_output(self, from_input=None, to_output=None, save=False):

        from_id = self._resolve_input_output_node_id(input=from_input)
        to_id = self._resolve_input_output_node_id(output=to_output)
        self._connect(from_id, to_id, save=save)

    ## Stream I/O

    def _write_to_stream(self, worker, data, output, tags=None, eos=True):
        # tags
        if tags is None:
            tags = []
        # auto-add HIDDEN
        tags.append("HIDDEN")

        # data
        output_stream = worker.write_data(data, output=output, id=self.id, tags=tags, scope="worker")

        # eos
        if eos:
            worker.write_eos(output=output, id=self.id, scope="worker")

        return output_stream

    def _write_data(self, worker, data, output, eos=True):
        return self._write_to_stream(worker, data, output, eos=eos)

    def _write_repr(self, worker, eos=True):
        return self._write_to_stream(worker, self._repr, "PLAN", tags=["PLAN"], eos=eos)

    def check_status(self, save=False):
        if self.leaves is None:
            self._detect_leaves()

        status = Status.FINISHED

        for leaf_id in self.leaves:
            leaf_node = self.get_node(leaf_id)
            leaf_stream = leaf_node['stream']
            if leaf_stream is None:
                status = Status.RUNNING
                break
            leaf_stream_status = self.get_stream_status(leaf_stream)
            if leaf_stream_status != Status.FINISHED:
                status = Status.RUNNING
                break

        self.set_status(status, save=save)
        return status

    def submit(self, worker):
        # process inputs with initialized values, if any
        nodes = self._repr['nodes']
        for node_id in nodes:
            node = nodes[node_id]

            # inputs
            if node['type'] == NodeType.INPUT:
                if node['value']:
                    data = node['value']
                    label = node['label']
                    # write data for input
                    stream = self._write_data(worker, data, label)
                    # set stream for node
                    self.set_node_stream(node_id, stream)
            # outputs
            if node['type'] == NodeType.OUTPUT:
                if node['value']:
                    data = node['value']
                    label = node['label']
                    # write data for output
                    stream = self._write_data(worker, data, label)
                    # set stream for node
                    self.set_node_stream(node_id, stream)

        # set status
        self.set_status(Status.SUBMITTED)

        # write plan
        self._write_repr(worker)
