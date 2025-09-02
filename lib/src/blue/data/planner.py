###### Parsers, Formats, Utils
import logging
import uuid

###### Blue
from blue.connection import PooledConnectionFactory
from blue.operators.registry import OperatorRegistry
from blue.data.pipeline import DataPipeline, NodeType, EntityType, Status


###############
### DataPlanner
#
class DataPlanner:
    def __init__(self, name="DATA_PLANNER", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):

        self.name = name
        if id:
            self.id = id
        else:
            self.id = str(hex(uuid.uuid4().fields[0]))[2:]

        if sid:
            self.sid = sid
        else:
            self.sid = self.name + ":" + self.id

        self.prefix = prefix
        self.suffix = suffix
        self.cid = cid

        if self.cid == None:
            self.cid = self.sid

            if self.prefix:
                self.cid = self.prefix + ":" + self.cid
            if self.suffix:
                self.cid = self.cid + ":" + self.suffix

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # search operator
        self.properties['operator_search'] = '/server/blue_ray/operator/operator_discover'

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def plan(self, input_data, task, context, approximate=False):
        # create a pipeline
        p = DataPipeline()

        # always create a plan with input, search, and output
        i = p.define_input(label="I", value=[[{"data": input_data}]])
        i.set_data("status", str(Status.EXECUTED))
        r = p.define_output(label="R")
        o = p.define_operator(self.properties['operator_search'], label="OD", attributes={"search_query": task, "approximate": True, "threshold": 0.8}, properties=self.properties)
        o.set_data("status", str(Status.INITED))
        p.connect_nodes(i, o)
        p.connect_nodes(o, r)

        # refine
        p = self.refine(p)

        return p

    def refine(self, p):
        operator_nodes = p.filter_nodes(filter_node_type=[NodeType.OPERATOR])

        for operator_id in operator_nodes:
            operator_node = p.get_node(operator_id)
            if operator_node.get_data("status") not in [Status.REFINED, Status.EXECUTING, Status.EXECUTED]:
                operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))
                operator_name = operator_entity.get_data("name")
                parsed = self.registry.parse_path(operator_name)

                # get input from previous
                ready = True
                prev_nodes = p.get_prev_nodes(operator_node)
                for prev_node in prev_nodes:
                    prev_node_status = prev_node.get_data("status")
                    if prev_node_status not in [Status.REFINED, Status.EXECUTED]:
                        ready = False
                        break

                if not ready:
                    continue

                # aggregate inputs form each prev node
                input_data = []
                prev_nodes = p.get_prev_nodes(operator_node)
                for prev_node in prev_nodes:
                    prev_node_status = prev_node.get_data("status")
                    prev_node_value = prev_node.get_data("value")

                    # TODO: check value fit
                    # TODO: mapping...
                    input_data += prev_node_value

                # refine
                kwargs = {"input_data": input_data, "attributes": operator_entity.get_data("attributes"), "properties": operator_entity.get_data("properties")}

                print(kwargs)
                # TODO: replace with refine function
                refinement = self.registry.execute_operator(parsed['operator'], parsed['server'], None, kwargs)
                print(refinement)
                # update status as refined

        return p

    def optimize(self, p, budget):
        # no optimization
        return p

    ######
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _start(self):
        self._start_connection()

        # initialize registry
        self._init_registry()

    def _init_registry(self):
        # create instance of agent registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id

        self.registry = OperatorRegistry(id=self.properties['operator_registry.name'], prefix=prefix, properties=self.properties)
