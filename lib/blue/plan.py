    
###### Parsers, Utils
import json

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.session import Session
from blue.stream import Constant, ControlCode
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, json_utils


###############
### Status
class Status(Constant):
    def __init__(self, c):
        super().__init__(c)

Status.INITED = Status("INITED")
Status.PLANNED = Status("PLANNED")
Status.RUNNING = Status("RUNNING")
Status.FINISHED = Status("FINISHED")

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
        self._plan_spec = {"id": self.id, "nodes": {}, "edges": {}, "streams": {}, "context": { "scope": self.prefix }, "properties": self.properties, "label2id": {} }

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
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()


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
            if 'edges' not in plan_spec:
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
            label = label + ".OUTPUT:" + input

        return label
    
    def define_input(self, name, label=None, value=None, stream=None, properties={}, save=False):
        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        if label is None:
            label = name
        node['label'] = label
        node['type'] = "INPUT"
        node['value'] = value
        node['stream'] = stream
        node['properties'] = properties
        node['parent'] = None
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # check
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._plan_spec['label2id']:
            raise Exception("Name should be unique")
        if label and label in self._plan_spec['label2id']:
            raise Exception("Labels should be unique")
        
        # add to plan
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][name] = id 
        # save
        if save:
            self.save(path="$.nodes." + id)
            self.save(path="$.label2id." + label)
            self.save(path="$.label2id." + name)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)


        return id

    def define_output(self, name, label=None, value=None, stream=None, properties={}, save=False):
        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        if label is None:
            label = name
        node['label'] = label
        node['type'] = "OUTPUT"
        node['value'] = value
        node['stream'] = stream
        node['properties'] = properties
        node['parent'] = None
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # check
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._plan_spec['label2id']:
            raise Exception("Name should be unique")
        if label and label in self._plan_spec['label2id']:
            raise Exception("Labels should be unique")
        
        # add to plan
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][name] = id 
        # save
        if save:
            self.save(path="$.nodes." + id)
            self.save(path="$.label2id." + label)
            self.save(path="$.label2id." + name)

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

        return id

    def define_agent(self, name, label=None, properties={}, save=False):
        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        if label is None:
            label = name
        node['label'] = label
        node['type'] = "AGENT"
        node['value'] = None
        node['stream'] = None
        node['properties'] = properties
        node['parent'] = None
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # check
        if name is None:
            raise Exception("Name is not specified")
        if name and name in self._plan_spec['label2id']:
            raise Exception("Name should be unique")
        if label and label in self._plan_spec['label2id']:
            raise Exception("Labels should be unique")
        
        # add to plan
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][name] = id
        # save
        if save:
            self.save(path="$.nodes." + id)
            self.save(path="$.label2id." + label)
            self.save(path="$.label2id." + name)

        return id

    def define_agent_input(self, name, agent, label=None, stream=None, properties={}, save=False):
        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        node['name'] = name
        default_label = self._get_default_label(agent, input=name)
        if label is None:
            label = default_label
        node['label'] = label
        node['type'] = "AGENT.INPUT"
        node['value'] = None
        node['stream'] = None
        node['properties'] = properties
        
        agent_id = None
        if agent in self._plan_spec['nodes']:
            agent_id = agent
        else:
            agent_node = self.get_node_by_label(agent)
            if agent_node:
                agent_id = agent_node['id']
        if agent_id is None:
            raise Exception("Agent is not in plan")
        else:
            agent_node['children'].append(id)

        node['parent'] = agent_id
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # check
        if name is None:
            raise Exception("Name is not specified")
        if default_label and default_label in self._plan_spec['label2id']:
            raise Exception("Labels should be unique")
        if label and label in self._plan_spec['label2id']:
            raise Exception("Labels should be unique")
        
        # add to plan
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][default_label] = id
        # save
        if save:
            self.save(path="$.nodes." + id)
            self.save(path="$.label2id." + label)     
            self.save(path="$.label2id." + default_label)    
            self.save(path="$.nodes." + agent_id + ".children")

        # add stream, if assigned
        if stream:
            self.set_node_stream(label, stream, save=save)

    def define_agent_output(self, name, agent, label=None, properties={}, save=False):        
        # create node
        node = {}
        id = node['id'] = uuid_utils.create_uuid()
        default_label = self._get_default_label(agent, output=name)
        node['name'] = name
        if label is None:
            label = default_label
        node['label'] = label
        node['type'] = "AGENT.OUTPUT"
        node['value'] = None
        node['stream'] = None
        node['properties'] = properties

        agent_id = None
        if agent in self._plan_spec['nodes']:
            agent_id = agent
        else:
            agent_node = self.get_node_by_label(agent)
            if agent_node:
                agent_id = agent_node['id']
        if agent_id is None:
            raise Exception("Agent is not in plan")
        else:
            agent_node['children'].append(id)

        node['parent'] = agent_id
        node['children'] = []
        node['prev'] = []
        node['next'] = []

        # add to plan
        self._plan_spec['nodes'][id] = node
        self._plan_spec['label2id'][label] = id 
        self._plan_spec['label2id'][default_label] = id
        # save
        if save:
            self.save(path="$.nodes." + id)
            self.save(path="$.label2id." + label)     
            self.save(path="$.label2id." + default_label)    
            self.save(path="$.nodes." + agent_id + ".children")

    def get_node_by_id(self, id):
        if id in self._plan_spec['nodes']:
            return self._plan_spec['nodes'][id]
        
    def get_node_by_label(self, label):
        if label in self._plan_spec['label2id']:
            id = self._plan_spec['label2id'][id]
            return self.get_node_by_id(id)
        
    def get_node_by_stream(self, stream):
        if stream in self._plan_spec['streams']:
            id = self._plan_spec['streams'][stream]['node']
            return self.get_node_by_id(id)
        
    def get_node(self, n):
        node = None
        if n in self._plan_spec['nodes']:
            node = self.get_node_by_id(n)
        else:
            node = self.get_node_by_label(n)
        return node

    def get_streams(self):
        return self._plan_spec['streams']
    
    def set_node_value(self, n, value, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Value for non-existing node cannot be set")
        
        node['value'] = value

        if save:
            id = node['id']
            self.save(path="$.nodes." + id + ".value")


    def set_node_stream(self, n, stream, status=None, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Stream for non-existing node cannot be set")
        
        node['stream'] = stream
        id = node['id']

        if status is None:
            status = Status.INITED

        self._plan_spec['streams'][stream] = { "node": id, "status": status }

        if save:
            self.save(path="$.nodes." + id + ".stream")
            self.save(path="$.streams." + stream)
        

    
    def set_node_properties(self, n, properties, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")
        
        node['properties'] = properties

        if save:
            self.save(path="$.nodes." + id + ".properties")

    def set_node_property(self, n, property, value, save=False):
        node = self.get_node(n)
        if node is None:
            raise Exception("Properties for non-existing node cannot be set")
        
        properties = node['properties']
        properties[property] = value

        if save:
            self.save(path="$.nodes." + id + ".properties." + property)

    def set_stream_status(self, stream, status, save=False):
        if stream in self._plan_spec['streams']:
             self._plan_spec['streams'][stream]['status'] = status

        if save:
            self.save(path="$.streams." + stream + ".status")

    def get_stream_status(self, stream):
        if stream in self._plan_spec['streams']:
            return self._plan_spec['streams'][stream]['status']
        else:
            return None

    # TODO
    def stream_in_plan(self, stream):
        stream_prefix = self.get_scope() + ":" + self.sid
        if stream.find(stream_prefix) == 0:
            s = stream[len(stream_prefix) :]
            ss = s.split(":")
            agent = ss[0]
            param = ss[3]

            # TODO: assigned labels are problematic, 
            # Need to maintain agent.param to label
            label = agent + "." + param

            # TODO: if label is in plan
            node = None 
            if canonical_name in canonical2id:
                id = canonical2id[canonical_name]
                self.set_data(plan_id + ".stream2id." + stream, id)
                return True

        return False 
    
    def parse_stream(self, stream):
        if self.match_stream(stream):
        else
            return None
        stream_prefix = self.get_scope() + ":" + self.sid



    def _get_default_edge_label(self, from_label, to_label):
        return from_label + ">" + to_label
    
    def _extract_nodes_from_edge_label(self, edge_label):
        return tuple(edge_label.split(">"))

    def _connect(self, from_label, to_label):
        edges = self._plan_spec['edges']
        nodes = self._plan_spec['nodes']

        if from_label not in nodes:
            raise Exception("Non-existing node cannot be connected")
        if to_label not in nodes:
            raise Exception("Non-existing node cannot be connected")

        edge_label = self._get_default_edge_label(from_label, to_label)
        if edge_label in edges:
            raise Exception("Connection already exists")
        
        edge_node = {
            'from': from_label,
            'to': to_label
        }

        edges[edge_label] = edge_node

        from_node = nodes[from_label]
        to_node = nodes[to_label]

        from_node['next'].append(to_label)
        to_node['prev'].append(from_label)

    def connect_input_to_agent(self, from_input_label=None, to_agent_input_label=None, to_agent=None, to_agent_input=None):
        nodes = self._plan_spec['nodes']

        if from_input_label:
            if from_input_label not in nodes:
                raise Exception("Non-existing input cannot be connected")
        else:
            raise Exception("Input should be specified")
        
        if to_agent_input_label:
            if to_agent_input_label not in nodes:
                raise Exception("Non-existing agent input cannot be connected")
        else:
            if to_agent:
                if to_agent not in nodes:
                    raise Exception("Non-existing agent cannot be connected")
            else:
                raise Exception("Agent should be specified")
            
            if to_agent_input is None:
                to_agent_input = "DEFAULT"

            to_agent_input_label = self._get_default_label(to_agent, input=to_agent_input)
            if to_agent_input_label not in nodes:
                raise Exception("Non-existing agent input cannot be connected")

        from_label = from_input_label
        to_label = to_agent_input_label

        self._connect(from_label, to_label)


    def connect_agent_to_output(self, from_agent_output_label=None, from_agent=None, from_agent_output=None, to_output_label=None):
        nodes = self._plan_spec['nodes']

        if to_output_label not in nodes:
            raise Exception("Non-existing output cannot be connected")
        
        if from_agent_output_label:
            if from_agent_output_label not in nodes:
                raise Exception("Non-existing agent output cannot be connected")
        else:
            if from_agent:
                if from_agent not in nodes:
                    raise Exception("Non-existing agent cannot be connected")
            else:
                raise Exception("Agent should be specified")
            
            if from_agent_output is None:
                from_agent_output = "DEFAULT"

            from_agent_output_label = self._get_default_label(from_agent, output=from_agent_output)
            if from_agent_output_label not in nodes:
                raise Exception("Non-existing agent output cannot be connected")
     
        from_label = from_agent_output_label
        to_label = to_output_label

        self._connect(from_label, to_label)

    def connect_agent_to_agent(self, from_agent_output_label=None, from_agent=None, from_agent_output=None, to_agent_input_label=None, to_agent=None, to_agent_input=None):
        nodes = self._plan_spec['nodes']

        if from_agent_output_label:
            if from_agent_output_label not in nodes:
                raise Exception("Non-existing agent output cannot be connected")
        else:
            if from_agent:
                if from_agent not in nodes:
                    raise Exception("Non-existing agent cannot be connected")
            else:
                raise Exception("Agent should be specified")
            
            if from_agent_output is None:
                from_agent_output = "DEFAULT"

            from_agent_output_label = self._get_default_label(from_agent, output=from_agent_output)
            if from_agent_output_label not in nodes:
                raise Exception("Non-existing agent output cannot be connected")
            
            if to_agent:
                if to_agent not in nodes:
                    raise Exception("Non-existing agent cannot be connected")
            else:
                raise Exception("Agent should be specified")
            
            if to_agent_input is None:
                to_agent_input = "DEFAULT"

            to_agent_input_label = self._get_default_label(to_agent, input=to_agent_input)
            if to_agent_input_label not in nodes:
                raise Exception("Non-existing agent input cannot be connected")
     
        from_label = from_agent_output_label
        to_label = to_agent_input_label

        self._connect(from_label, to_label)       


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

    def _write_plan_spec(self, worker, eos=True):
        return self._write_to_stream(worker, self._plan_spec, "PLAN", tags=["PLAN"], eos=eos)

    def submit(self, worker):
        # process inputs with initialized values, if any
        nodes = self._plan_spec['nodes']
        for node_label in nodes:
            node = nodes[node_label]
            # inputs
            if node['type'] == "INPUT":
                input_label = node_label
                if node['value']:
                    data = node['value']
                    # write data for input
                    input_stream = self._write_data(worker, data, input_label)
                    # set stream for input
                    self.set_node_stream(input_label, input_stream)
            # outputs
            if node['type'] == "OUTPUT":
                output_label = node_label
                if node['value']:
                    data = node['value']
                    # write data for output
                    output_stream = self._write_data(worker, data, output_label)
                    # set stream for input
                    self.set_node_stream(output_label, output_stream)


        # write plan
        self._write_plan_spec(worker)

    # persistence
    def _get_plan_data_namespace(self):
        return self.cid + ":DATA"
    
    def save(self, path=None):
        if path is None:
            path = "$"

        data = json_utils.json_query(self._plan_spec, path, single=True)

        self.connection.json().set(
            self._get_plan_data_namespace(),
            path,
            data,
            nx=True,
        )



        

