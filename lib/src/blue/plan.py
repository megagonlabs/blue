    
###### Parsers, Utils
import json
import logging

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.session import Session
from blue.stream import Constant, ControlCode, ConstantEncoder
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, json_utils


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


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

NodeType.INPUT = Status("INPUT")
NodeType.OUTPUT = Status("OUTPUT")
NodeType.AGENT = Status("AGENT")
NodeType.AGENT_INPUT = Status("AGENT_INPUT")
NodeType.AGENT_OUTPUT = Status("AGENT_OUTPUT")

###############
### Plan
#
class Plan:
    def __init__(self, id=None, scope=None, properties={}):
        
        self.name = "PLAN"
        
        if id:
            self.id = id
        else:
            self.id = uuid_utils.create_uuid()

        self.sid = self.name + ":" + self.id

        if type(scope) == str:
            self.prefix = scope
        elif type(scope) == Session:
            self.prefix = scope.cid
            
        self.suffix = None
        self.cid = None

        if self.cid == None:
            self.cid = self.sid

            if self.prefix:
                self.cid = self.prefix + ":" + self.cid
            if self.suffix:
                self.cid = self.cid + ":" + self.suffix
        
 
        self._initialize(properties=properties)

        # plan spec details
        self._plan_spec = {"id": self.id, "nodes": {}, "streams": {}, "context": { "scope": self.prefix }, "status": Status.INACTIVE, "properties": self.properties, "label2id": {} }

        # start
        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None, save=False):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

        if save:
            self.save(path="$.properties")

    def _start(self):
        self._start_connection()

        self.leaves = None


    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()


    @classmethod
    def _verify_plan_spec(cls, plan_spec):
        # TODO: Do more verification, in regards to steps, context streams
        if type(plan_spec) == dict:
            if 'id' not in plan_spec:
                return None
            if 'nodes' not in plan_spec:
                return None
            if 'streams' not in plan_spec:
                return None
            if 'context' not in plan_spec:
                return None
            context = plan_spec['context']
            if 'scope' not in context:
                return None 
        else:
            return None
        return plan_spec
    
    # build a declaratively, from a json spec
    @classmethod
    def from_json(cls, plan_spec, save=False):
        if type(plan_spec) == str:
            try:
                plan_spec = json.loads(plan_spec)
            except:
                plan_spec = None 
        
        # verify plan
        plan_spec = Plan._verify_plan_spec(plan_spec)

        if plan_spec:
            id = plan_spec['id']
            scope = plan_spec['context']['scope']
            properties = plan_spec['properties']

            # create instance
            plan = cls(id=id, scope=scope, properties=properties)

            # set spec
            plan._plan_spec = plan_spec

            if save:
                plan.save()

            # return 
            return plan
        else:
            raise Exception("Invalid plan spec")

    def to_json(self):
        return json.dumps(self._plan_spec)


    def get_scope(self):
        return self._plan_spec['context']['scope']

    def _get_default_label(self, agent, input=None, output=None):
        label = agent

        if input:
            label = label + ".INPUT:" + input
        elif output:
            label = label + ".OUTPUT:" + output

        return label
    
    def set_status(self, status, save=False):
        self._plan_spec['status'] = status

        # save
        if save:
            self.save(path="$.status")

    def get_status(self):
        return self._plan_spec['status'] 
    


        

    def define_input(self, name, label=None, value=None, stream=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._plan_spec['label2id']:
            raise Exception("Name should be unique")
        if label and label in self._plan_spec['label2id']:
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
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][name] = id 
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.label2id['" + label + "']")
            self.save(path="$.label2id['" + name + "']")

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

        return node

    def define_output(self, name, label=None, value=None, stream=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._plan_spec['label2id']:
            raise Exception("Name should be unique")
        if label and label in self._plan_spec['label2id']:
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
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][name] = id 
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.label2id['" + label + "']")
            self.save(path="$.label2id['" + name + "']")

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

        return node

    def define_agent(self, name, label=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._plan_spec['label2id']:
            raise Exception("Name should be unique")
        if label and label in self._plan_spec['label2id']:
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
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][name] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.label2id['" + label + "']")
            self.save(path="$.label2id['" + name + "']")

        return node

    def define_agent_input(self, name, agent, label=None, stream=None, properties={}, save=False):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if agent is None:
            raise Exception("Agent is not specified")
        if label and label in self._plan_spec['label2id']:
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

        if default_label and default_label in self._plan_spec['label2id']:
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
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][default_label] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.label2id['" + label + "']")
            self.save(path="$.label2id['" + default_label + "']")   
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
        if label and label in self._plan_spec['label2id']:
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

        if default_label and default_label in self._plan_spec['label2id']:
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
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][default_label] = id
        # save
        if save:
            self.save(path="$.nodes[']" + id + "']")
            self.save(path="$.label2id['" + label + "']")
            self.save(path="$.label2id['" + default_label + "']")   
            self.save(path="$.nodes['" + agent_id + "'].children")

        return node
    
    # node functions
    def get_node_by_id(self, id):
        if id in self._plan_spec['nodes']:
            return self._plan_spec['nodes'][id]
        
    def get_node_by_label(self, label):
        if label in self._plan_spec['label2id']:
            id = self._plan_spec['label2id'][label]
            return self.get_node_by_id(id)
        
    def get_nodes_by_stream(self, stream, node_type=None):
        nodes = []
        if stream in self._plan_spec['streams']:
            ids = self._plan_spec['streams'][stream]['nodes']
            for id in ids:
                node = self.get_node(id)
                if node_type:
                    if type(node_type) == list:
                        if node['type'] in node_type:
                            nodes.append(node)
                    else:
                        if node['type'] == node_type:
                            nodes.append(node)
                else:
                    nodes.append(node)
        return nodes
        
    def get_node(self, n):
        node = None
        if n in self._plan_spec['nodes']:
            node = self.get_node_by_id(n)
        else:
            node = self.get_node_by_label(n)
        return node

    def get_nodes(self):
        return self._plan_spec['nodes']

    def is_node_leaf(self, n):
        node = self.get_node(n)
        prev = node['prev']
        next = node['next']

        if len(prev) > 0 and len(next) == 0:
            return True
        else:
            return False

    def get_streams(self):
        return self._plan_spec['streams']
    
    def get_node_value(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be get")
        
        value = node['value']

        if value is None:
            return fetch_node_value_from_stream(n)

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

        if stream in self._plan_spec['streams']:
            # add node
            self._plan_spec['streams'][stream]['nodes'].append(id)
        else:            
            self._plan_spec['streams'][stream] = { "nodes": [id], "status": Status.INITED, "value": None }

        if save:
            self.save(path="$.nodes['" + id + "'].stream")
            self.save(path="$.streams['" + stream + "']")
        
    def get_node_stream(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Stream for non-existing node cannot be get")

        return node['stream']

    def get_node_properties(self, n):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be get")

        return node['properties']
    
    def get_node_property(self, n, property):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be get")

        properties = node['properties']
        if property in properties:
            return properties[property]
        else:
            return None
        
    def set_node_properties(self, n, properties, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")
        
        node['properties'] = properties

        if save:
            self.save(path="$.nodes['" + id + "'].properties")

    def set_node_property(self, n, property, value, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")
        
        properties = node['properties']
        properties[property] = value

        if save:
            self.save(path="$.nodes['" + id + "'].properties['" + property + "']")

    def get_node_type(self, n):
        node = self.get_node(n)

        return node['type']
    
    def get_parent_node(self, n):
        node = self.get_node(n)

        parent_id = node['parent']
        parent_node = self.get_node_by_id(parent_id)
        
        return parent_node
    
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


    # stream functions
    def set_stream_status(self, stream, status, save=False):
        if stream in self._plan_spec['streams']:
            self._plan_spec['streams'][stream]['status'] = status

            if save:
                self.save(path="$.streams['" + stream + "'].status")

    def get_stream_status(self, stream):
        if stream in self._plan_spec['streams']:
            return self._plan_spec['streams'][stream]['status']
        else:
            return None

    def set_stream_value(self, stream, value, save=False):
        if stream in self._plan_spec['streams']:
            self._plan_spec['streams'][stream]['value'] = value

            if save:
                self.save(path="$.streams['" + stream + "'].value")

    def append_stream_value(self, stream, value, save=False):
        if stream in self._plan_spec['streams']:
            va = self._plan_spec['streams'][stream]['value']
            if va is None:
                va = []
                self._plan_spec['streams'][stream]['value'] = va
            
            va.append(value)

            if save:
                self.save(path="$.streams['" + stream + "'].value")

    def get_stream_value(self, stream):
        if stream in self._plan_spec['streams']:
            return self._plan_spec['streams'][stream]['value']
        else:
            return None
        
    # stream discovery 
    def match_stream(self, stream):
        node = None
        stream_prefix = self.get_scope() + ":" + self.sid
        if stream.find(stream_prefix) == 0:
            s = stream[len(stream_prefix) + 1:]
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
    def _safe_json(self, o):
        if type(o) == dict:
            s = json.dumps(o, cls=ConstantEncoder)
            return json.loads(s)
        elif isinstance(o, Constant):
            return str(o)
        else:
            return o
    
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

    def _write_plan_spec(self, worker, eos=True):
        return self._write_to_stream(worker, self._plan_spec, "PLAN", tags=["PLAN"], eos=eos)

    def _detect_leaves(self):
        self.leaves = []

        nodes = self.get_nodes()
        for node_id in nodes:
            if self.is_node_leaf(node_id):
                self.leaves.append(node_id)

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


    def submit(self, worker):
        # process inputs with initialized values, if any
        nodes = self._plan_spec['nodes']
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
        self._write_plan_spec(worker)

    # persistence
    def _get_plan_data_namespace(self):
        return self.cid + ":DATA"
    
    def save(self, path=None):
        if path is None:
            path = "$"

        data = json_utils.json_query(self._plan_spec, path, single=True)

        safe_data = self._safe_json(data)
        
        self.connection.json().set(
            self._get_plan_data_namespace(),
            path,
            safe_data
        )



        

