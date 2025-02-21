    
###### Parsers, Utils
import json

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.session import Session
from blue.stream import ControlCode
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils

###############
### Plan
#
class Plan:
    def __init__(self, scope=None, properties={}):
        
        self.name = "PLAN"
        
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
        
        # plan spec details
        self._values = {}
        self._plan_spec = {"id": self.id, "steps": [], "context": { "scope": self.prefix, "streams": {} }}

        self._initialize(properties=properties)

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

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _verify_plan_spec(self, plan_spec):
        # TODO: Do more verification, in regards to steps, context streams
        if type(plan_spec) == dict:
            if 'id' not in plan_spec:
                return None
            if 'steps' not in plan_spec:
                return None
            if 'context' not in plan_spec:
                return None
            context = plan_spec['context']
            if 'scope' not in context:
                return None 
            if 'streams' not in context:
                return None
        else:
            return None
        return plan_spec
    
    # build a declaratively, from a json spec
    def from_json(self, plan_spec):
        if type(plan_spec) == str:
            try:
                plan_spec = json.loads(plan_spec)
            except:
                plan_spec = None 
        plan_spec = self._verify_plan_spec(plan_spec)
        if plan_spec:
            # set plan spec
            self._plan_spec = plan_spec

    def to_json(self):
        return self._plan_spec
    
    def set_scope(self, scope):
        self._scope = scope 

    def _get_canonical(self, agent, param):
        return agent + "." + param
    
    def set_input_value(self, input, value):
        self._values[input] = value

    def set_input_stream(self, input, stream):
        streams = self._plan_spec["context"]["streams"]
        streams[input] = stream

    def _add_step(self, f, t):
        steps = self._plan_spec['steps']
        steps.append([f, t])

    def add_input_to_agent_step(self, input, to_agent, to_param=None):
        if to_param is None:
            to_param = "DEFAULT"

        t = self._get_canonical(to_agent, to_param)
        self._add_step(input, t)

    def add_agent_to_agent_step(self, from_agent, to_agent, from_param=None, to_param=None):
        if from_param is None:
            from_param = "DEFAULT"
        if to_param is None:
            to_param = "DEFAULT"

        f = self._get_canonical(from_agent, from_param)
        t = self._get_canonical(to_agent, to_param)

        self._add_step(f, t)

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
        # process values, if any
        for i in self._values:
            v = self._values[i]
            # write v for i
            s = self._write_data(worker, v, i)
            # set s for i
            self.set_input_stream(i, s)

        # write plan
        self._write_plan_spec(worker)

    def _start(self):
        # TODO: For future work
        pass