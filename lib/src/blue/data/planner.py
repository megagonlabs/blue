###### Parsers, Formats, Utils
import logging
import uuid, json

###### Blue
from blue.constant import Constant
from blue.connection import PooledConnectionFactory
from blue.operators.registry import OperatorRegistry
from blue.data.pipeline import DataPipeline, NodeType, EntityType, Status
from blue.utils import json_utils


class TaskType(Constant):
    def __init__(self, c):
        super().__init__(c)


TaskType.QUESTION_ANSWER = NodeType("QUESTION_ANSWER")
TaskType.DATA_TRANSFORM = NodeType("DATA_TRANSFORM")


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
        self.properties['plan_discover_operator'] = '/server/blue_ray/operator/plan_discover'

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def plan(self, plan_data, plan_task, plan_attributes):

        p = None

        if plan_task == TaskType.QUESTION_ANSWER:

            ## build attributes
            pipeline_attributes = {}
            pipeline_attributes = json_utils.merge(pipeline_attributes, plan_attributes)
            pipeline_attributes['task'] = str(TaskType.QUESTION_ANSWER)
            pipeline_attributes['data'] = plan_data

            # create a pipeline
            p = DataPipeline(attributes=pipeline_attributes, properties=self.properties)

            # input = [[]] for question answer
            i = p.define_input(value=[[]], provenance=p.get_id())
            i.set_data("status", str(Status.EXECUTED))
            # operator: use plan discover as specified in the properties

            ## map pipeline attributes to plan_discover operator attributes
            plan_discover_attributes = {}
            plan_discover_attributes['task'] = pipeline_attributes['task']
            plan_discover_attributes['data'] = pipeline_attributes['data']

            # additional attributes
            plan_discover_attributes['approximate'] = True
            plan_discover_attributes['threshold'] = 0.75

            # set plan discover operator as defined in planner properties
            o = p.define_operator(self.properties['plan_discover_operator'], attributes=plan_discover_attributes)
            o.set_data("status", str(Status.INITED))

            # output
            r = p.define_output()

            # set plan input / output
            p.set_plan_input(i)
            p.set_plan_output(r)

            # connections: input -> plan_search -> output
            p.connect_nodes(i, o)
            p.connect_nodes(o, r)

        elif plan_task == TaskType.DATA_TRANSFORM:
            pass
        else:
            raise Exception("Unknown task for planner")

        if p is None:
            raise Exception("No plan generated")

        return p

    def print_node_queue(self, p, queue):
        queue_contents = []
        for node_id in queue:
            node = p.get_node(node_id)
            node_status = node.get_data("status")
            node_type = node.get_type()

            queue_content = ""
            if node_type == NodeType.INPUT:
                queue_content += "INPUT [" + node_id + "]"
            elif node_type == NodeType.OUTPUT:
                queue_content += "OUTPUT [" + node_id + "]"
            elif node_type == NodeType.OPERATOR:
                operator_entity = p.get_node_entity(node, str(EntityType.OPERATOR))
                operator_name = "unknown"
                operator_id = "unknown"
                if operator_entity:
                    operator_name = operator_entity.get_data("name")
                    operator_id = operator_entity.get_id()
                    queue_content += "OPERATOR [" + node_id + ":" + operator_name + "(" + operator_id + ")]"

            queue_content += "(" + str(node_status) + ")"
            queue_contents.append(queue_content)

        print("[ " + " | ".join(queue_contents) + " ]")

    def propogate_failure_recursively(self, p, n, provenance="$"):
        # set status as failed
        p.set_node_status(n, str(Status.FAILED), provenance=provenance)

        # propogate status to next nodes
        next_nodes = p.get_next_nodes(n)

        for next_node in next_nodes:
            self.propogate_failure_recursively(p, next_node, provenance=provenance)

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
            # no pipelines, nothing to propogate further up
            if pipelines is None:
                return
            # more than one pipeline, do not propogate further up
            # TODO: what if all pipelines failed, how to identify that situation?
            if len(pipelines) > 1:
                return

            # single valid pipeline failed, so parent node should also fail
            operator_nodes = p.get_nodes_by_entity(operator_entity)
            for operator_node in operator_nodes:
                self.propogate_failure_recursively(p, operator_node, provenance=provenance)

    def get_inherited_properties(self, p, operator_node):
        inherited_properties = {}

        operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))

        ## check if part of pipeline
        parent_pipeline = p.get_node_entity(operator_node, str(EntityType.DATA_PIPELINE))

        if parent_pipeline:
            parent_pipeline_properties = p.get_data("properties")

            # TODO: map
            mapped_parent_pipeline_properties = parent_pipeline_properties
            # inherit
            inherited_properties = json_utils.merge_json(inherited_properties, mapped_parent_pipeline_properties)

            # parent operator
            # parent_operator_entity_id = parent_pipeline.get_data("parent")
            # parent_operator_entity = p.get_entity(parent_operator_entity_id)

            # if parent_operator_entity:
            #     parent_operator_name = parent_operator_entity.get_data("name")
            #     parent_operator_properties = parent_operator_entity.get_data("properties")

            #     # TODO: map
            #     mapped_parent_operator_properties = parent_operator_properties
            #     # inherit
            #     inherited_properties = json_utils.merge_json(inherited_properties, mapped_parent_operator_properties)

        return inherited_properties

    def get_inherited_attributes(self, p, operator_node):
        inherited_attributes = {}

        operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))

        ## check if part of pipeline
        parent_pipeline = p.get_node_entity(operator_node, str(EntityType.DATA_PIPELINE))

        if parent_pipeline:
            parent_pipeline_attributes = p.get_data("attributes")

            # map
            mapped_parent_pipeline_attributes = self.map_pipeline_to_operator_attributes(parent_pipeline_attributes, operator_entity)
            # merge
            inherited_attributes = json_utils.merge_json(inherited_attributes, mapped_parent_pipeline_attributes)

            # parent operator
            parent_operator_entity_id = parent_pipeline.get_data("parent")
            parent_operator_entity = p.get_entity(parent_operator_entity_id)

            if parent_operator_entity:
                parent_operator_attributes = parent_operator_entity.get_data("attributes")

                # map
                mapped_parent_operator_attributes = self.map_operator_to_opearator_attributes(parent_operator_attributes, operator_entity, parent_operator_entity)
                # merge
                inherited_attributes = json_utils.merge_json(inherited_attributes, mapped_parent_operator_attributes)

        return inherited_attributes

    def map_pipeline_to_operator_attributes(self, parent_pipeline_attributes, operator_entity):
        operator_name = operator_entity.get_data("name")
        parsed = self.registry.parse_path(operator_name)
        operator_name = parsed['operator']
        operator_server = parsed['server']

        # print("mapping pipeline attributes to operator attributes:")
        # print("operator name: " + operator_name)
        # print("operator server: " + operator_server)
        # print("pipeline attributes: " + json.dumps(parent_pipeline_attributes))

        # TODO:
        mappped_parent_pipeline_attributes = parent_pipeline_attributes
        # print("mapped pipeline attributes: " + json.dumps(mappped_parent_pipeline_attributes))

        return mappped_parent_pipeline_attributes

    def map_operator_to_opearator_attributes(self, parent_operator_attributes, operator_entity, parent_operator_entity):
        operator_name = operator_entity.get_data("name")
        parsed = self.registry.parse_path(operator_name)
        operator_name = parsed['operator']
        operator_server = parsed['server']

        parent_operator_name = parent_operator_entity.get_data("name")
        parsed = self.registry.parse_path(parent_operator_name)
        parent_operator_name = parsed['operator']
        parent_operator_server = parsed['server']

        # print("mapping parent operator attributes to operator attributes:")
        # print("operator name: " + operator_name)
        # print("operator server: " + operator_server)
        # print("parent operator name: " + parent_operator_name)
        # print("parent operator server: " + parent_operator_server)

        # print("parent operator attributes: " + json.dumps(parent_operator_attributes))

        # TODO: llm based mapper
        mappped_parent_operator_attributes = {}
        if operator_name == "question_answer" and parent_operator_name == "plan_discover":
            mappped_parent_operator_attributes['question'] = parent_operator_attributes["data"]
        elif operator_name == "query_breakdown" and parent_operator_name == "question_answer":
            mappped_parent_operator_attributes['query'] = parent_operator_attributes["question"]
        else:
            mappped_parent_operator_attributes = parent_operator_attributes

        # print("mapped parent operator attributes: " + json.dumps(mappped_parent_operator_attributes))

        return mappped_parent_operator_attributes

    def execute(self, p):
        plan_input_node = p.get_plan_input()
        provenance = p.get_data("provenance")

        self.execute_recursively(p, plan_input_node, provenance=provenance)

    # helper functions for execution and refinement
    def aggregate_inputs(self, p, n, provenance=None):
        ## state
        ready = True
        failed = False

        ## inputs: aggregate input form each prev node,
        input_data = []
        prev_nodes = p.get_prev_nodes(n)
        for prev_node in prev_nodes:
            prev_node_status = p.get_node_status(prev_node, provenance=provenance)
            if prev_node_status in [Status.FAILED]:
                failed = True
                ready = False
                return None, ready, failed
            if prev_node_status not in [Status.EXECUTED]:
                ready = False
                return None, ready, failed

            prev_node_value = p.get_node_value(prev_node, provenance=provenance)
            if prev_node_value is None:
                ready = False
                return None, ready, failed
            input_data += prev_node_value

        return input_data, ready, failed

    def get_node_pipeline_entity(self, p, n):
        return p.get_node_entity(n, str(EntityType.DATA_PIPELINE))

    def get_node_parent_operator_entity(self, p, n):
        pipeline_entity = self.get_node_pipeline_entity(p, n)
        if pipeline_entity:
            parent_operator_entity_id = pipeline_entity.get_data("parent")
            if parent_operator_entity_id:
                return p.get_entity(parent_operator_entity_id)
        return None

    def get_node_parent_operator_node(self, p, n):
        parent_operator_entity = self.get_node_parent_operator_entity(p, n)
        if parent_operator_entity:
            operator_nodes = p.get_nodes_by_entity(parent_operator_entity)
            # should be only one
            for operator_node in operator_nodes:
                return operator_node
        return None

    def execute_recursively(self, p, node, provenance="$"):

        node_id = node.get_id()

        # get node type
        node_type = node.get_type()

        # get node status
        node_status = p.get_node_status(node, provenance=provenance)

        print("-------------------------")
        print("processing node: " + str(node_type) + "[" + node_id + "]")

        # identify pipeline entity, parent operator entity and node, if part of pipeline
        pipeline_entity = self.get_node_pipeline_entity(p, node)
        parent_operator_entity = self.get_node_parent_operator_entity(p, node)
        parent_operator_node = self.get_node_parent_operator_node(p, node)

        # aggregate input_value
        input_data, ready, failed = self.aggregate_inputs(p, node, provenance=provenance)

        # failed, propogate error, stop
        if failed:
            self.propogate_failure_recursively(p, node, provenance=provenance)
            return

        if node_type == NodeType.INPUT:
            # set status
            p.set_node_status(node, str(Status.EXECUTED), provenance=provenance)

            # continue so we can process next
        elif node_type == NodeType.OUTPUT:
            # set status
            p.set_node_status(node, str(Status.EXECUTED), provenance=provenance)
            # set value
            p.set_node_value(node, input_data, provenance=provenance)

            # copy value to parent node, continue
            if parent_operator_node:
                # set parent value
                p.set_node_value(parent_operator_node, input_data, provenance=provenance)
                # continue with parent_operator
                self.execute_recursively(p, parent_operator_node, provenance=provenance)

            return
        elif node_type == NodeType.OPERATOR:
            # if value set, continue
            v = p.get_node_value(node, provenance=provenance)
            if v:
                # already refined and value received from sub plans, so go on...
                if node_status in [Status.FAILED]:
                    return
                # continue so we can process next
            else:
                operator_node = node
                operator_id = node_id

                # operator entity
                operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))
                operator_entity_id = operator_entity.get_id()

                # operator name
                operator_name = operator_entity.get_data("name")
                print("processing operator: " + operator_name + " [" + operator_entity_id + "]")

                # parse full operator name to extract name and server
                parsed = self.registry.parse_path(operator_name)
                operator_name = parsed['operator']
                operator_server = parsed['server']

                registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)

                # check operator can be refined
                refine = False
                if 'refine' in registry_properties and registry_properties['refine']:
                    refine = True

                operator_properties = {}
                planner_properties = self.properties
                registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)
                inherited_properties = self.get_inherited_properties(p, operator_node)

                operator_properties = json_utils.merge_json(operator_properties, planner_properties)
                operator_properties = json_utils.merge_json(operator_properties, registry_properties)
                operator_properties = json_utils.merge_json(operator_properties, inherited_properties)
                operator_properties = json_utils.merge_json(operator_properties, operator_entity.get_data("properties"))

                ## attributes
                operator_attributes = {}
                inherited_operator_attributes = self.get_inherited_attributes(p, operator_node)
                operator_attributes = json_utils.merge_json(operator_attributes, inherited_operator_attributes)
                operator_attributes = json_utils.merge_json(operator_attributes, operator_entity.get_data("attributes"))

                ## operator function parameters
                kwargs = {"input_data": input_data, "attributes": operator_attributes, "properties": operator_properties}
                print(kwargs)

                # refine or execute
                if refine:
                    ### refine
                    print("refining...")
                    p.set_node_status(operator_node, str(Status.REFINING), provenance=provenance)
                    subplans = self.registry.refine_operator(operator_name, operator_server, None, kwargs)

                    # print("plans:")
                    # print(subplans)
                    if subplans is None:
                        print("no subplan, error")
                        # failed
                        self.propogate_failure_recursively(p, operator_node, provenance=provenance)
                        return
                    else:
                        # set status
                        p.set_node_status(operator_node, str(Status.REFINED), provenance=provenance)

                        # set pipelines
                        operator_entity.set_data("pipelines", [])

                        # merge plans, and execute
                        for subplan in subplans:
                            try:
                                sp = DataPipeline.from_dict(subplan)
                                operator_entity.append_data("pipelines", sp.get_id())
                                sp.set_data("parent", operator_entity.get_id())
                                p.merge(sp)

                                subplan_provenance = provenance + "." + sp.get_id()
                                ### execute subplans starting from their plan input
                                plan_input_node = p.get_plan_input(pipeline=sp.get_id())
                                p.set_node_value(plan_input_node, input_data, provenance=subplan_provenance)
                                self.execute_recursively(p, plan_input_node, provenance=subplan_provenance)
                                return
                            except:
                                print("invalid subplan, error")
                                # failed
                                self.propogate_failure_recursively(p, operator_node, provenance=provenance)
                                return

                else:
                    ### execute
                    print("executing...")
                    output = self.registry.execute_operator(operator_name, operator_server, None, kwargs)
                    # print("output:")
                    # print("None" if output is None else json.dumps(output))
                    if output is None:
                        # failed
                        self.propogate_failure_recursively(p, operator_node, provenance=provenance)
                        return

        # execute next nodes
        next_nodes = p.get_next_nodes(node)
        for next_node in next_nodes:
            self.execute_recursively(p, next_node, provenance=provenance)

    # def execute(self, p, queue=None):
    #     if queue is None:
    #         # get plan input
    #         plan_input_id = p.get_plan_input_id()

    #         # create queue and add
    #         queue = []
    #         queue.append(plan_input_id)
    #         self.execute(p, queue=queue)

    #     else:
    #         # queue archive
    #         queue_archive = set(queue)

    #         while len(queue) > 0:
    #             node_id = queue.pop(0)
    #             node = p.get_node(node_id)

    #             # get node type / status
    #             node_type = node.get_type()
    #             node_status = node.get_data("status")

    #             print("-------------------------")
    #             print("processing node: " + node_id + " " + str(node_status))

    #             if node_status is None:
    #                 node.set_data("status", str(Status.INITED))
    #                 node_status = node.get_data("status")

    #             # executed, add nexts to the queue
    #             if node_status in [Status.EXECUTED]:
    #                 # add next nodes to the queue
    #                 next_nodes = p.get_next_nodes(node)
    #                 for next_node in next_nodes:
    #                     queue.append(next_node.get_id())
    #                 continue

    #             ### process node by type
    #             if node_type == NodeType.OPERATOR:

    #                 ### refine or execute operator
    #                 # set operator node
    #                 operator_node = node
    #                 operator_id = node_id
    #                 operator_provenance = operator_node.get_data("provenance")

    #                 # operator entity
    #                 operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))
    #                 operator_entity_id = operator_entity.get_id()

    #                 # operator name
    #                 operator_name = operator_entity.get_data("name")
    #                 print("processing operator: " + operator_name + " [" + operator_entity_id + "]")

    #                 # parse full operator name to extract name and server
    #                 parsed = self.registry.parse_path(operator_name)
    #                 operator_name = parsed['operator']
    #                 operator_server = parsed['server']

    #                 registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)

    #                 # check operator can be refined
    #                 refine = False
    #                 if 'refine' in registry_properties and registry_properties['refine']:
    #                     refine = True
    #                     operator_node.set_data("status", str(Status.REFINING))

    #                 if not refine:
    #                     planned = True
    #                     operator_node.set_data("status", str(Status.PLANNED))

    #                 # ready, if  all input is ready/executed
    #                 ready = True
    #                 prev_nodes = p.get_prev_nodes(operator_node)

    #                 failed = False
    #                 for prev_node in prev_nodes:
    #                     prev_node_status = prev_node.get_data("status")
    #                     if prev_node_status in [Status.FAILED]:
    #                         failed = True
    #                         break

    #                     if prev_node_status not in [Status.EXECUTED]:
    #                         ready = False

    #                 # failed
    #                 if failed:
    #                     operator_node.set_data("status", str(Status.FAILED))
    #                     # propogage error
    #                     self.propogate_error(p, operator_node)
    #                     continue

    #                 # do not execute or refine, if not ready
    #                 if not ready:
    #                     # set previous nodes status to PLANNED for next iteration
    #                     for prev_node in prev_nodes:
    #                         prev_node_status = prev_node.get_data("status")

    #                         if prev_node_status not in [Status.EXECUTED]:

    #                             prev_node_id = prev_node.get_id()
    #                             prev_node.set_data("status", str(Status.PLANNED))
    #                             # add prev node to the queue, if not there
    #                             if prev_node_id not in queue:
    #                                 queue.append(prev_node_id)

    #                     # put current operator back in queue too
    #                     print("not ready!")
    #                     queue.append(operator_id)
    #                     continue

    #                 ###### proceed to refine/execute
    #                 #### operator details
    #                 ## inputs: aggregate input form each prev node,
    #                 input_data = []
    #                 prev_nodes = p.get_prev_nodes(operator_node)
    #                 for prev_node in prev_nodes:
    #                     prev_node_status = prev_node.get_data("status")
    #                     prev_node_value = p.get_node_value(prev_node, provenance=operator_provenance)
    #                     input_data += prev_node_value

    #                 ## properties
    #                 operator_properties = {}
    #                 planner_properties = self.properties
    #                 registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)
    #                 inherited_properties = self.get_inherited_properties(p, operator_node)

    #                 operator_properties = json_utils.merge_json(operator_properties, planner_properties)
    #                 operator_properties = json_utils.merge_json(operator_properties, registry_properties)
    #                 operator_properties = json_utils.merge_json(operator_properties, inherited_properties)
    #                 operator_properties = json_utils.merge_json(operator_properties, operator_entity.get_data("properties"))

    #                 ## attributes
    #                 operator_attributes = {}
    #                 inherited_operator_attributes = self.get_inherited_attributes(p, operator_node)
    #                 operator_attributes = json_utils.merge_json(operator_attributes, inherited_operator_attributes)
    #                 operator_attributes = json_utils.merge_json(operator_attributes, operator_entity.get_data("attributes"))

    #                 ## operator function parameters
    #                 kwargs = {"input_data": input_data, "attributes": operator_attributes, "properties": operator_properties}
    #                 print(kwargs)

    #                 # set
    #                 operator_entity.set_data("attributes", operator_attributes)
    #                 operator_entity.set_data("properties", operator_properties)

    #                 # refine
    #                 if refine:
    #                     # add additional pipeline context (attributes and properties) to kwargs
    #                     print("refining...")
    #                     subplans = self.registry.refine_operator(operator_name, operator_server, None, kwargs)
    #                     # print("plans:")
    #                     # print(subplans)
    #                     if subplans is None:
    #                         # nothing to refine, skip
    #                         print("nothing to refine, skip")
    #                         continue

    #                     # set pipelines
    #                     operator_entity.set_data("pipelines", [])

    #                     # merge plans
    #                     for subplan in subplans:
    #                         try:
    #                             sp = DataPipeline.from_dict(subplan)
    #                             operator_entity.append_data("pipelines", sp.get_id())
    #                             sp.set_data("parent", operator_entity.get_id())
    #                             p.merge(sp, operator_provenance)
    #                         except:
    #                             # invalid plan, skip
    #                             print("invalid subplan, skip")
    #                             continue

    #                     # update status as refined
    #                     operator_node.set_data("status", str(Status.REFINED))

    #                     # TODO: add new operators to queue (in any order, so should be ordered...)
    #                     o_dict = p.filter_nodes(filter_node_type=[NodeType.OPERATOR])
    #                     for o_id in o_dict:
    #                         if o_id in queue_archive:
    #                             continue
    #                         else:
    #                             queue.append(o_id)
    #                             queue_archive.add(o_id)

    #                 elif planned:
    #                     # set status as executing
    #                     print("executing...")
    #                     operator_node.set_data("status", str(Status.EXECUTING))

    #                     # execute
    #                     output = self.registry.execute_operator(operator_name, operator_server, None, kwargs)
    #                     # print("output:")
    #                     # print("None" if output is None else json.dumps(output))
    #                     if output is None:
    #                         operator_node.set_data("status", str(Status.FAILED))
    #                         # propogage error
    #                         self.propogate_error(p, operator_node)
    #                     else:
    #                         # update status as executed
    #                         operator_node.set_data("status", str(Status.EXECUTED))

    #                     # set value by provenance
    #                     p.set_node_value(output, provenance=operator_provenance)

    #             elif node_type == NodeType.INPUT:
    #                 # TODO: carry over value
    #                 pass
    #             elif node_type == NodeType.OUTPUT:
    #                 # TODO: carry over value [needs more thinking]
    #                 # check if parent / pipeline set value according
    #                 # set parent as planned, to the queue
    #                 pass

    #             print("---------")
    #             print(p.get_data())
    #             input("continue")

    # def refine(self, p):
    #     # build operator queue for refine / execute

    #     operators_dict = p.filter_nodes(filter_node_type=[NodeType.OPERATOR])
    #     operator_queue = list(operators_dict.keys())

    #     # operator queue archive
    #     operator_queue_archive = set(operator_queue)

    #     while len(operator_queue) > 0:
    #         print("-------------------------")
    #         self.print_node_queue(p, operator_queue)
    #         # print("operator_queue count:" + str(len(operator_queue)))

    #         # get top in queue
    #         operator_id = operator_queue.pop(0)
    #         operator_node = p.get_node(operator_id)

    #         # operator entity
    #         operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))

    #         # operator name
    #         operator_name = operator_entity.get_data("name")

    #         # get status
    #         operator_status = operator_node.get_data("status")
    #         if operator_status is None:
    #             operator_node.set_data("status", str(Status.INITED))
    #             operator_status = operator_node.get_data("status")

    #         print("-------------------------")
    #         print("processing: " + operator_name + " [" + operator_id + "] " + str(operator_status))

    #         # do not refine/execute if done already
    #         if operator_status not in [Status.REFINED, Status.EXECUTED]:

    #             # parse full operator name to extract name and server
    #             parsed = self.registry.parse_path(operator_name)
    #             operator_name = parsed['operator']
    #             operator_server = parsed['server']

    #             registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)

    #             # check if operator is planned for execution in refine
    #             planned = operator_status == str(Status.PLANNED)

    #             # check operator can be refined
    #             refine = False
    #             if 'refine' in registry_properties and registry_properties['refine']:
    #                 refine = True

    #             # no need to refine/execute
    #             if not planned and not refine:
    #                 continue

    #             # ready, if  all input is ready/executed
    #             ready = True
    #             prev_nodes = p.get_prev_nodes(operator_node)

    #             failed = False
    #             for prev_node in prev_nodes:
    #                 prev_node_status = prev_node.get_data("status")
    #                 if prev_node_status in [Status.FAILED]:
    #                     failed = True
    #                     break

    #                 if prev_node_status not in [Status.REFINED, Status.EXECUTED]:
    #                     ready = False

    #             # failed
    #             if failed:
    #                 operator_node.set_data("status", str(Status.FAILED))
    #                 # propogage error
    #                 self.propogate_error(p, operator_node)
    #                 continue

    #             # do not execute or refine, if not ready
    #             if not ready:
    #                 # set previous nodes status to PLANNED for next iteration
    #                 for prev_node in prev_nodes:
    #                     prev_node_status = prev_node.get_data("status")

    #                     if prev_node_status not in [Status.REFINED, Status.EXECUTED]:
    #                         # set previous node status to PLANNED for next iteration,

    #                         prev_node_id = prev_node.get_id()
    #                         prev_node.set_data("status", str(Status.PLANNED))
    #                         # add prev node to the queue, if not there
    #                         if prev_node_id not in operator_queue:
    #                             operator_queue.append(prev_node_id)

    #                 # put current operator back in queue too
    #                 print("not ready!")
    #                 operator_queue.append(operator_id)
    #                 continue

    #             ###### proceed to refine/execute
    #             #### operator details
    #             ## inputs: aggregate input form each prev node,
    #             input_data = []
    #             prev_nodes = p.get_prev_nodes(operator_node)
    #             for prev_node in prev_nodes:
    #                 prev_node_status = prev_node.get_data("status")
    #                 prev_node_value = prev_node.get_data("value")
    #                 input_data += prev_node_value

    #             ## properties
    #             operator_properties = {}
    #             planner_properties = self.properties
    #             registry_properties = self.registry.get_record_properties(operator_name, type="operator", scope="/server/" + operator_server)
    #             inherited_properties = self.get_inherited_properties(p, operator_node)

    #             operator_properties = json_utils.merge_json(operator_properties, planner_properties)
    #             operator_properties = json_utils.merge_json(operator_properties, registry_properties)
    #             operator_properties = json_utils.merge_json(operator_properties, inherited_properties)
    #             operator_properties = json_utils.merge_json(operator_properties, operator_entity.get_data("properties"))

    #             ## attributes
    #             operator_attributes = {}
    #             inherited_operator_attributes = self.get_inherited_attributes(p, operator_node)
    #             operator_attributes = json_utils.merge_json(operator_attributes, inherited_operator_attributes)
    #             operator_attributes = json_utils.merge_json(operator_attributes, operator_entity.get_data("attributes"))

    #             ## operator function parameters
    #             kwargs = {"input_data": input_data, "attributes": operator_attributes, "properties": operator_properties}
    #             # print(kwargs)

    #             # set
    #             operator_entity.set_data("attributes", operator_attributes)
    #             operator_entity.set_data("properties", operator_properties)

    #             # refine
    #             if refine:
    #                 # add additional pipeline context (attributes and properties) to kwargs

    #                 print("refining...")
    #                 subplans = self.registry.refine_operator(operator_name, operator_server, None, kwargs)
    #                 # print("plans:")
    #                 # print(subplans)
    #                 if subplans is None:
    #                     # nothing to refine, skip
    #                     print("nothing to refine, skip")
    #                     continue

    #                 # set pipelines
    #                 operator_entity.set_data("pipelines", [])

    #                 # merge plans, create mux/demux nodes
    #                 for subplan in subplans:
    #                     try:
    #                         sp = DataPipeline.from_dict(subplan)
    #                         operator_entity.append_data("pipelines", sp.get_id())
    #                         sp.set_data("parent", operator_entity.get_id())
    #                         p.merge(sp)
    #                     except:
    #                         # invalid plan, skip
    #                         print("invalid subplan, skip")
    #                         continue

    #                 # update status as refined
    #                 operator_node.set_data("status", str(Status.REFINED))

    #                 # TODO: add new operators to queue (in any order, so should be ordered...)
    #                 o_dict = p.filter_nodes(filter_node_type=[NodeType.OPERATOR])
    #                 for o_id in o_dict:
    #                     if o_id in operator_queue_archive:
    #                         continue
    #                     else:
    #                         operator_queue.append(o_id)
    #                         operator_queue_archive.add(o_id)

    #             # execute
    #             elif planned:
    #                 # set status as executing
    #                 print("executing...")
    #                 operator_node.set_data("status", str(Status.EXECUTING))

    #                 # execute
    #                 output = self.registry.execute_operator(operator_name, operator_server, None, kwargs)
    #                 # print("output:")
    #                 # print("None" if output is None else json.dumps(output))
    #                 if output is None:
    #                     operator_node.set_data("status", str(Status.FAILED))
    #                     # propogage error
    #                     self.propogate_error(p, operator_node)
    #                 else:
    #                     # update status as executed
    #                     operator_node.set_data("status", str(Status.EXECUTED))

    #                 # set value
    #                 operator_node.set_data("value", output)

    #         print("---------")
    #         print(p.get_data())
    #         input("continue")
    #     return p

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
