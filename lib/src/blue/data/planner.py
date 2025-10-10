###### Parsers, Formats, Utils
import logging
import uuid, json

import traceback
import logging

###### Blue
from blue.constant import Constant
from blue.connection import PooledConnectionFactory
from blue.operators.registry import OperatorRegistry
from blue.data.pipeline import DataPipeline, NodeType, EntityType, Status
from blue.utils import json_utils


class TaskType(Constant):
    """Task types for DataPlanner:

    - QUESTION_ANSWER: for question answering tasks
    - DATA_TRANSFORM: for data transformation tasks (Not implemented yet)
    """

    def __init__(self, c):
        super().__init__(c)


TaskType.QUESTION_ANSWER = NodeType("QUESTION_ANSWER")
TaskType.DATA_TRANSFORM = NodeType("DATA_TRANSFORM")


###############
### DataPlanner
#
class DataPlanner:
    """Data planner to create and execute data processing pipelines based on tasks and data.
    It uses an operator registry to discover and refine operators for the tasks, and builds a data pipeline accordingly.
    This is currently a simple rule-based planner, but can be extended to use LLMs for more complex planning.
    Currently supports QUESTION_ANSWER task type.

    !!! note
        This is an experimental feature and may change in future releases.
    """

    def __init__(self, name="DATA_PLANNER", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        """Initialize DataPlanner with optional name, id, sid, cid, prefix, suffix, and properties.

        Parameters:
            name (str): Name of the planner.
            id (str): Unique identifier for the planner. If not provided, a random UUID is generated.
            sid (str): Short identifier. If not provided, constructed from name and id.
            cid (str): Canonical identifier. If not provided, constructed from sid, prefix, and  suffix.
            prefix (str): Optional prefix for cid.
            suffix (str): Optional suffix for cid.
            properties (dict): Properties for the planner.
        """
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
        """
        Initialize the planner with default and provided properties.

        Parameters:
            properties: Properties for the planner. Defaults to None.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        """
        Initialize default properties for the planner.
        """
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # search operator
        self.properties['plan_discover_operator'] = '/server/blue_ray/operator/plan_discover'

    def _update_properties(self, properties=None):
        """
        Update the planner properties with provided properties.

        Parameters:
            properties: Properties to update. Defaults to None.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def plan(self, plan_data, plan_task, plan_attributes):
        """Create a data processing plan based on the task, data, and attributes.
        In current implementation, only supports QUESTION_ANSWER task type, and simply relies on a predefined plan_discover operator.
        This can be extended to use LLMs for more complex planning in future.

        Parameters:
            plan_data (str): The data to be processed.
            plan_task (TaskType): The type of task to be performed.
            plan_attributes (dict): Additional attributes for the plan.
        """
        p = None

        if plan_task == TaskType.QUESTION_ANSWER:

            ## build attributes
            pipeline_attributes = {}
            pipeline_attributes = json_utils.merge(pipeline_attributes, plan_attributes)
            pipeline_attributes['task'] = str(TaskType.QUESTION_ANSWER)
            pipeline_attributes['data'] = plan_data

            # create a pipeline
            logging.info("> Creating pipeline")
            logging.info("    Plan task: " + pipeline_attributes['task'])
            logging.info("    Plan data: " + pipeline_attributes['data'])
            logging.debug("    Attributes: " + json.dumps(pipeline_attributes, indent=3))
            p = DataPipeline(attributes=pipeline_attributes, properties=self.properties)

            # input = [[]] for question answer
            i = p.define_input(value=[[]], provenance="$." + p.get_id())
            i.set_data("status", str(Status.INITED))
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

            # output
            r = p.define_output()

            # set plan input / output
            p.set_plan_input(i)
            p.set_plan_output(r)

            # connections: input -> plan_search -> output
            p.connect_nodes(i, o)
            p.connect_nodes(o, r)

            logging.debug("    Plan: " + json.dumps(p.get_data(), indent=3))

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

        logging.debug("[ " + " | ".join(queue_contents) + " ]")

    def propogate_failure_recursively(self, p, n, provenance="$"):
        """Propogate failure status recursively to next nodes and parent nodes if applicable.

        Parameters:
            p (DataPipeline): The data pipeline.
            n (Node): The current node where failure occurred.
            provenance (str): Provenance string for tracking. Defaults to "$"."
        """
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
        """Get inherited properties for an operator node from its parent pipeline and parent operator if applicable.

        Parameters:
            p (DataPipeline): The data pipeline.
            operator_node (Node): The operator node to get inherited properties for.

        Returns:
            dict: Inherited properties.
        """
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
        """Get inherited attributes for an operator node from its parent pipeline and parent operator if applicable.

        Parameters:
            p (DataPipeline): The data pipeline.
            operator_node (Node): The operator node to get inherited attributes for.

        Returns:
            dict: Inherited attributes.
        """
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
        """Map parent pipeline attributes to operator attributes.
        This is a placeholder function and currently does not perform any mapping.

        Parameters:
            parent_pipeline_attributes (dict): Attributes of the parent pipeline.
            operator_entity (Entity): The operator entity to map attributes for.

        Returns:
            dict: Mapped operator attributes."""
        operator_name = operator_entity.get_data("name")
        parsed = self.registry.parse_path(operator_name)
        operator_name = parsed['operator']
        operator_server = parsed['server']

        # logging.debug("> Mapping pipeline attributes to operator attributes:")
        # logging.debug("    Operator name: " + operator_name)
        # logging.debug("    Operator server: " + operator_server)
        # logging.debug("    Pipeline attributes: " + json.dumps(parent_pipeline_attributes))

        # TODO:
        mappped_parent_pipeline_attributes = parent_pipeline_attributes
        # logging.debug("    Mapped pipeline attributes: " + json.dumps(mappped_parent_pipeline_attributes))

        return mappped_parent_pipeline_attributes

    def map_operator_to_opearator_attributes(self, parent_operator_attributes, operator_entity, parent_operator_entity):
        """Map parent operator attributes to operator attributes.
        This is a simple rule-based mapper based on operator names.

        Parameters:
            parent_operator_attributes (dict): Attributes of the parent operator.
            operator_entity (Entity): The operator entity to map attributes for.
            parent_operator_entity (Entity): The parent operator entity.

        Returns:
            dict: Mapped operator attributes.
        """
        operator_name = operator_entity.get_data("name")
        parsed = self.registry.parse_path(operator_name)
        operator_name = parsed['operator']
        operator_server = parsed['server']

        parent_operator_name = parent_operator_entity.get_data("name")
        parsed = self.registry.parse_path(parent_operator_name)
        parent_operator_name = parsed['operator']
        parent_operator_server = parsed['server']

        logging.debug("> Mapping parent operator attributes to operator attributes:")
        logging.debug("    Operator name: " + operator_name)
        logging.debug("    Operator server: " + operator_server)
        logging.debug("    Parent operator name: " + parent_operator_name)
        logging.debug("    Parent operator server: " + parent_operator_server)

        logging.debug("    Parent operator attributes: " + json.dumps(parent_operator_attributes))

        # TODO: llm based mapper
        mappped_parent_operator_attributes = {}
        if operator_name == "nl2llm" and parent_operator_name == "plan_discover":
            mappped_parent_operator_attributes['query'] = parent_operator_attributes["data"]
        elif operator_name == "nl2sql" and parent_operator_name == "plan_discover":
            mappped_parent_operator_attributes['question'] = parent_operator_attributes["data"]
        elif operator_name == "question_answer" and parent_operator_name == "plan_discover":
            mappped_parent_operator_attributes['question'] = parent_operator_attributes["data"]
        elif operator_name == "query_breakdown" and parent_operator_name == "question_answer":
            mappped_parent_operator_attributes['query'] = parent_operator_attributes["question"]
        else:
            mappped_parent_operator_attributes = parent_operator_attributes

        logging.debug("    Mapped parent operator attributes: " + json.dumps(mappped_parent_operator_attributes))

        return mappped_parent_operator_attributes

    def execute(self, p):
        """
        Execute the data pipeline recursively starting from the plan input node.

        Parameters:
            p (DataPipeline): The data pipeline to execute.
        """
        plan_input_node = p.get_plan_input()
        provenance = p.get_data("provenance") + "." + p.get_id()

        self.execute_recursively(p, plan_input_node, provenance=provenance)

        logging.debug("    Executed Plan: " + json.dumps(p.get_data(), indent=3))

        o = p.get_plan_output()

        values = p.get_node_values(o)
        logging.info("    Output: " + json.dumps(values, indent=3))
        logging.info("\n")
        return values

    # helper functions for execution and refinement
    def aggregate_inputs(self, p, n, provenance=None):
        """
        Aggregate inputs from previous nodes for the current node to prepare for execution.

        Parameters:
            p (DataPipeline): The data pipeline.
            n (Node): The current node to aggregate inputs for.
            provenance (str): Provenance string for tracking. Defaults to None.

        Returns:
            tuple: A tuple containing:
                - input_data (list): Aggregated input data from previous nodes.
                - ready (bool): Whether the current node is ready for execution.
                - failed (bool): Whether any previous node has failed.
        """
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
        """
        Get the pipeline entity for a given node if it is part of a pipeline.

        Parameters:
            p (DataPipeline): The data pipeline.
            n (Node): The node to get the pipeline entity for.

        Returns:
            Entity: The pipeline entity if the node is part of a pipeline, otherwise None.
        """
        return p.get_node_entity(n, str(EntityType.DATA_PIPELINE))

    def get_node_parent_operator_entity(self, p, n):
        """
        Get the parent operator entity for a given node if it is part of a pipeline.

        Parameters:
            p (DataPipeline): The data pipeline.
            n (Node): The node to get the parent operator entity for.

        Returns:
            Entity: The parent operator entity if the node is part of a pipeline, otherwise None.
        """
        pipeline_entity = self.get_node_pipeline_entity(p, n)
        if pipeline_entity:
            parent_operator_entity_id = pipeline_entity.get_data("parent")
            if parent_operator_entity_id:
                return p.get_entity(parent_operator_entity_id)
        return None

    def get_node_parent_operator_node(self, p, n):
        """
        Get the parent operator node for a given node if it is part of a pipeline.

        Parameters:
            p (DataPipeline): The data pipeline.
            n (Node): The node to get the parent operator node for.

        Returns:
            Node: The parent operator node if the node is part of a pipeline, otherwise None.
        """
        parent_operator_entity = self.get_node_parent_operator_entity(p, n)
        if parent_operator_entity:
            operator_nodes = p.get_nodes_by_entity(parent_operator_entity)
            # should be only one
            for operator_node in operator_nodes:
                return operator_node
        return None

    def execute_recursively(self, p, node, provenance="$"):
        """
        Execute a node and its children recursively, updating statuses and handling failures as needed.
        Provenance is used to track the execution path and passed on recursively.

        Parameters:
            p (DataPipeline): The data pipeline.
            node (Node): The node to execute.
            provenance (str): The provenance string.
        """
        node_id = node.get_id()

        # get node type
        node_type = node.get_type()

        # get node status
        node_status = p.get_node_status(node, provenance=provenance)

        logging.info("\n")
        logging.info("> Executing...")
        logging.info("    Provenance: " + provenance)
        logging.info("    Processing node: " + str(node_type) + "[" + node_id + "]")

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

        # not ready, do not run
        if not ready:
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
                # mark as executed, continue so we can process next
                p.set_node_status(parent_operator_node, str(Status.EXECUTED), provenance=provenance)
                # continue with parent_operators nexts
                parent_next_nodes = p.get_next_nodes(parent_operator_node)
                for parent_next_node in parent_next_nodes:
                    self.execute_recursively(p, parent_next_node, provenance=provenance)

            # no next node, so return
            return
        elif node_type == NodeType.OPERATOR:
            # if value set, continue
            v = p.get_node_value(node, provenance=provenance)
            if v:
                # already refined and value received from sub plans, so go on...
                if node_status in [Status.FAILED]:
                    return
            else:
                operator_node = node
                operator_id = node_id

                # operator entity
                operator_entity = p.get_node_entity(operator_node, str(EntityType.OPERATOR))
                operator_entity_id = operator_entity.get_id()

                # operator name
                operator_name = operator_entity.get_data("name")
                logging.info("    Processing operator: " + operator_name + " [" + operator_entity_id + "]")

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
                logging.info("    kwargs: " + json.dumps(json_utils.summarize_json(kwargs)))
                logging.debug(kwargs)

                # set attributes, properties
                operator_entity.set_data("attributes", operator_attributes)
                operator_entity.set_data("properties", operator_properties)

                # refine or execute
                if refine:
                    ### refine
                    logging.info("    Refining...")
                    p.set_node_status(operator_node, str(Status.REFINING), provenance=provenance)
                    subplans = self.registry.refine_operator(operator_name, operator_server, None, kwargs)

                    logging.debug("    Subplans:")
                    logging.debug("    " + json.dumps(subplans, indent=3))
                    if subplans is None:
                        logging.error("    No subplan, error!")
                        # failed
                        self.propogate_failure_recursively(p, operator_node, provenance=provenance)
                        return
                    else:
                        # set status
                        p.set_node_status(operator_node, str(Status.REFINED), provenance=provenance)

                        # set pipelines
                        operator_entity.set_data("pipelines", [])

                        # merge plans, and executes
                        subplan_ids = []
                        for subplan in subplans:
                            sp = DataPipeline.from_dict(subplan)
                            operator_entity.append_data("pipelines", sp.get_id())
                            sp.set_data("parent", operator_entity.get_id())
                            p.merge(sp)
                            subplan_ids.append(sp.get_id())

                        # execute plans recursively
                        for subplan_id in subplan_ids:
                            # subplan provenance
                            subplan_provenance = provenance + "." + subplan_id
                            ### execute subplans starting from their plan input
                            plan_input_node = p.get_plan_input(pipeline=subplan_id)
                            p.set_node_value(plan_input_node, input_data, provenance=subplan_provenance)
                            self.execute_recursively(p, plan_input_node, provenance=subplan_provenance)
                        return

                else:
                    ### execute
                    logging.info("    Executing...")
                    p.set_node_status(operator_node, str(Status.EXECUTING), provenance=provenance)
                    output = self.registry.execute_operator(operator_name, operator_server, None, kwargs)
                    logging.info("   Summary Output: " + json.dumps(json_utils.summarize_json(output, depth_limit=5, list_limit=5, key_limit=10)))
                    logging.debug("    Output:")
                    logging.debug("    " + "None" if output is None else json.dumps(output))
                    if output is None:
                        # failed
                        self.propogate_failure_recursively(p, operator_node, provenance=provenance)
                        return
                    else:
                        # set status
                        p.set_node_status(operator_node, str(Status.EXECUTED), provenance=provenance)
                        # set operator value
                        p.set_node_value(operator_node, output, provenance=provenance)

        # execute next nodes
        next_nodes = p.get_next_nodes(node)
        for next_node in next_nodes:
            self.execute_recursively(p, next_node, provenance=provenance)

    def optimize(self, p, budget):
        """
        Optimize the data pipeline based on the given budget.
        This is a placeholder function and currently does not perform any optimization.
        """
        # no optimization
        return p

    ######
    def _start_connection(self):
        """Start the database connection."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _start(self):
        """Start the planner by establishing database connection and initializing the operator registry."""
        self._start_connection()

        # initialize registry
        self._init_registry()

    def _init_registry(self):
        """Initialize the operator registry for the planner."""
        # create instance of agent registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id

        self.registry = OperatorRegistry(id=self.properties['operator_registry.name'], prefix=prefix, properties=self.properties)
