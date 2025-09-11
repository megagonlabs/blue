###### Parsers, Formats, Utils
import logging
import uuid, json

###### Blue
from blue.connection import PooledConnectionFactory
from blue.operators.registry import OperatorRegistry
from blue.data.pipeline import DataPipeline, NodeType, EntityType, Status
from blue.utils import json_utils


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
        self.properties['plan_search'] = '/server/blue_ray/operator/plan_discover'

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
        o = p.define_operator(self.properties['plan_search'], label="OD", attributes={"search_query": task, "approximate": True, "threshold": 0.90}, properties=self.properties)
        o.set_data("status", str(Status.INITED))
        p.connect_nodes(i, o)
        p.connect_nodes(o, r)

        # refine
        p = self.refine(p)

        return p

    def print_operator_queue(self, p, operator_queue):
        queue_contents = []
        for operator_id in operator_queue:
            operator_node = p.get_node(operator_id)
            operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))
            operator_name = operator_entity.get_data("name")
            queue_contents.append(operator_name)
        print("[" + "|".join(queue_contents) + "]")

    def propogate_error(self, p, n):
        # set status as  failed
        n.set_data("status", str(Status.FAILED))

        # propogate status to next nodes
        next_nodes = p.get_next_nodes(n)

        for next_node in next_nodes:
            self.propogate_error(p, next_node)

        # go up
        if len(next_nodes) == 0:
            pipeline_entity = p.get_node_entity(n, str(EntityType.DATA_PIPELINE))
            if pipeline_entity is None:
                return
            # check if has parent operator
            operator_entity_id = pipeline_entity.get_data("parent")
            if operator_entity_id is None:
                return
            operator_entity = p.get_entity(operator_entity_id)
            if operator_entity is None:
                return

            # check pipelines
            pipelines = operator_entity.get_data("pipelines")
            if pipelines is None:
                return
            if len(pipelines) > 1:
                return

            # single valid pipeline failed, so parent node should also fail
            operator_nodes = p.get_nodes_by_entity(operator_entity)
            for operator_node in operator_nodes:
                self.propogate_error(p, operator_node)

    def extract_attributes(self, input_data, operator_name, operator_server, operator_attributes):
        print("extracting attributes...")
        print("operator name:" + operator_name)
        print("operator server: " + operator_server)
        print("operator attributes: " + json.dumps(operator_attributes))
        print("input:" + json.dumps(input_data))

        # TODO: use registry get_operator_attributes to collect and use metadata for extraction

        if operator_name == "query_breakdown":
            operator_attributes['query'] = input_data[0][0]['data']

        print("operator attributes: " + json.dumps(operator_attributes))
        return operator_attributes

    def refine(self, p):

        operators_dict = p.filter_nodes(filter_node_type=[NodeType.OPERATOR])
        operator_queue = list(operators_dict.keys())

        while len(operator_queue) > 0:
            self.print_operator_queue(p, operator_queue)
            print("operator_queue count:" + str(len(operator_queue)))

            # get top in queue
            operator_id = operator_queue.pop(0)
            operator_node = operators_dict[operator_id]

            # operator entity
            operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))

            # operator name
            operator_name = operator_entity.get_data("name")
            print("processing: " + operator_name)

            # get status
            operator_status = operator_node.get_data("status")
            if operator_status is None:
                operator_node.set_data("status", str(Status.INITED))

            # do not refine/execute if done already
            if operator_status not in [Status.REFINED, Status.EXECUTING, Status.EXECUTED]:

                # parse full operator name to extract name and server
                parsed = self.registry.parse_path(operator_name)
                operator_name = parsed['operator']
                operator_server = parsed['server']

                #### operator details
                operator_properties = {}
                operator_attribues = operator_entity.get_data("attributes")

                ## build properties starting from planner
                planner_properties = self.properties
                registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)
                in_plan_properties = operator_entity.get_data("properties")
                operator_properties = json_utils.merge_json(operator_properties, planner_properties)
                operator_properties = json_utils.merge_json(operator_properties, registry_properties)
                operator_properties = json_utils.merge_json(operator_properties, in_plan_properties)

                # check if operator is planned for execution in refine
                planned = operator_status == str(Status.PLANNED)

                # check operator can be refined
                refine = False
                if 'refine' in operator_properties and operator_properties['refine']:
                    refine = True

                # no need
                if not planned and not refine:
                    continue

                # get input from previous
                ready = True
                prev_nodes = p.get_prev_nodes(operator_node)

                failed = False
                for prev_node in prev_nodes:
                    prev_node_status = prev_node.get_data("status")
                    if prev_node_status in [Status.FAILED]:
                        failed = True
                        break

                    if prev_node_status not in [Status.REFINED, Status.EXECUTED]:
                        ready = False

                        # set status to PLANNED for next iteration,
                        if refine:
                            prev_node_id = prev_node.get_id()
                            prev_node_name = prev_node.get_data("name")
                            prev_node.set_data("status", str(Status.PLANNED))
                            # add prev node to the queue, if not there
                            if prev_node_id not in operator_queue:
                                operator_queue.append(prev_node_id)

                # failed
                if failed:
                    operator_node.set_data("status", str(Status.FAILED))
                    # propogage error
                    self.propogate_error(p, operator_node)

                    continue

                # cannot execute or refine, if not ready
                if not ready:
                    # put back in queue
                    print("not ready!")
                    operator_queue.append(operator_id)
                    continue

                ## aggregate inputs form each prev node, compute input_data, attributes, and properties
                input_data = []
                prev_nodes = p.get_prev_nodes(operator_node)
                for prev_node in prev_nodes:
                    prev_node_status = prev_node.get_data("status")
                    prev_node_value = prev_node.get_data("value")

                    input_data += prev_node_value

                # map attributes
                operator_attribues = self.extract_attributes(input_data, operator_name, operator_server, operator_attribues)

                kwargs = {"input_data": input_data, "attributes": operator_attribues, "properties": operator_properties}
                print(kwargs)

                # refine
                if refine:
                    print("refining...")
                    subplans = self.registry.refine_operator(operator_name, operator_server, None, kwargs)

                    if subplans is None:
                        # nothing to refine, skip
                        print("nothing to refine, skip")
                        continue

                    # set pipelines
                    operator_entity.set_data("pipelines", [])

                    # merge plans
                    for subplan in subplans:
                        try:
                            sp = DataPipeline.from_dict(subplan)
                            operator_entity.append_data("pipelines", sp.get_id())
                            sp.set_data("parent", operator_entity.get_id())
                            p.merge(sp)
                        except:
                            # invalid plan, skip
                            print("invalid subplan, skip")
                            continue

                    # update status as refined
                    operator_node.set_data("status", str(Status.REFINED))

                    # add new operators to queue
                    o_dict = p.filter_nodes(filter_node_type=[NodeType.OPERATOR])
                    for o_id in o_dict:
                        if o_id in operators_dict:
                            continue
                        else:
                            operators_dict[o_id] = o_dict[o_id]
                            operator_queue.append(o_id)

                # execute
                elif planned:
                    # set status as executing
                    print("executing...")
                    operator_node.set_data("status", str(Status.EXECUTING))

                    # execute
                    output = self.registry.execute_operator(operator_name, operator_server, None, kwargs)

                    if output is None:
                        operator_node.set_data("status", str(Status.FAILED))
                        # propogage error
                        self.propogate_error(p, operator_node)
                    else:
                        # update status as executed
                        operator_node.set_data("status", str(Status.EXECUTED))

                    # set value
                    operator_node.set_data("value", output)

            print(p.get_data())
            input("continue")
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
