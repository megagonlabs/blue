###### Parsers, Formats, Utils
import time
import argparse
import logging
import time
import uuid
import pydash

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.constant import Constant
from blue.pubsub import Producer
from blue.stream import Message, MessageType, ContentType, ControlCode
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, log_utils, dag_utils


###############
### Status
class Status(Constant):
    """
    Status of a node in a data pipeline:

    - INITED: node is created, initialized (e.g., input data is not processed yet)
    - REFINING: node is being refined (e.g., input data is being processed for refinement)
    - REFINED: node is refined (e.g., input data is processed for refinement)
    - EXECUTING: node is being executed (e.g., operator is being executed)
    - EXECUTED: node is executed (e.g., operator has finished executing)
    - PLANNED: node is planned (e.g., operator is planned to be executed)
    - FAILED: node has failed (e.g., operator has failed to execute)
    """

    def __init__(self, c):
        super().__init__(c)


Status.INITED = Status("INITED")
Status.REFINING = Status("REFINING")
Status.REFINED = Status("REFINED")
Status.EXECUTING = Status("EXECUTING")
Status.EXECUTED = Status("EXECUTED")
Status.PLANNED = Status("PLANNED")
Status.FAILED = Status("FAILED")


class NodeType(Constant):
    """
    Type of a node in a data pipeline:

    - INPUT: node is an input node
    - OUTPUT: node is an output node
    - OPERATOR: node is an operator node
    """

    def __init__(self, c):
        super().__init__(c)


NodeType.INPUT = NodeType("INPUT")
NodeType.OUTPUT = NodeType("OUTPUT")
NodeType.OPERATOR = NodeType("OPERATOR")


class EntityType(Constant):
    """
    Type of an entity in a data pipeline:

    - OPERATOR: entity is an operator
    - DATA_PIPELINE: entity is a data pipeline
    """

    def __init__(self, c):
        super().__init__(c)


EntityType.OPERATOR = EntityType("OPERATOR")
EntityType.DATA_PIPELINE = EntityType("DATA_PIPELINE")


###############
### DataPipeline
#
class DataPipeline(dag_utils.Plan):
    """
    DataPipeline class to represent a data pipeline in the system, compromising of nodes (input, operators, output) and edges, representing the data flow between nodes.
    """

    def __init__(
        self,
        id=None,
        label=None,
        type="DATA_PIPELINE",
        properties=None,
        attributes=None,
        path=None,
        plan_provenance=None,
        plan_input=None,
        plan_output=None,
        synchronizer=None,
        auto_sync=False,
        sync=None,
    ):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)
        """ Initialize a DataPipeline object.
        
        Parameters:
            id (str): Unique identifier for the data pipeline. If None, a UUID will be generated.
            label (str): Label for the data pipeline.
            type (str): Type of the data pipeline. Default is "DATA_PIPELINE".
            properties (dict): Properties for the data pipeline.
            attributes (dict): Attributes for the data pipeline.
            path (str): Path in reference to synchronize the data pipeline.
            plan_provenance (str): Provenance string for the data pipeline.
            plan_input (str or Node): Input node or node ID for the data pipeline.
            plan_output (str or Node): Output node or node ID for the data pipeline.
            synchronizer: Synchronizer object to handle synchronization with the database.
            auto_sync (bool): Whether to automatically synchronize changes with the database.
            sync: Synchronization flag.
        """
        # plan_provenance
        if plan_provenance is None:
            plan_provenance = "$"
        self.set_plan_provenance(plan_provenance, sync=sync)

        # set plan input / output
        self.set_plan_input(plan_input, sync=sync)
        self.set_plan_output(plan_output, sync=sync)

        self._initialize_attributes(sync=sync)
        self._update_attributes(attributes=attributes, sync=sync)

    ### attributes
    def _initialize_attributes(self, sync=None):
        """
        Initialize attributes dictionary if not already present.

        Parameters:
            sync: Synchronization flag.
        """
        self.set_data("attributes", {}, sync=sync)

    def _update_attributes(self, attributes=None, sync=None):
        """
        Update attributes dictionary with new values.

        Parameters:
            attributes: Dictionary of attributes to update.
            sync: Synchronization flag.
        """
        if attributes is None:
            return

        # override
        for a in attributes:
            self.set_attribute(a, attributes[a], sync=sync)

    def set_attribute(self, key, value, sync=None):
        """
        Set an attribute for the data pipeline.

        Parameters:
            key (str): Attribute key.
            value: Attribute value.
            sync: Synchronization flag.
        """
        attributes = self.get_attributes()
        attributes[key] = value

        self.synchronize(key="attributes." + key, value=value)

    def get_attribute(self, key):
        """
        Get an attribute for the data pipeline.

        Parameters:
            key (str): Attribute key.

        Returns:
            value: Attribute value or None if not found.
        """
        attributes = self.get_attributes()
        if key in attributes:
            return attributes[key]
        return None

    def get_attributes(self):
        """
        Get all attributes for the data pipeline.

        Returns:
            (dict): Dictionary of attribute key-value pairs.
        """
        return self.get_data("attributes")

    # provenance
    def set_plan_provenance(self, plan_provenance, sync=None):
        """
        Set the plan provenance for the data pipeline.

        Parameters:
            plan_provenance (str): Plan provenance string.
            sync: Synchronization flag.
        """
        self.set_data("provenance", plan_provenance, sync=sync)

    def get_plan_provenance(self):
        """
        Get the plan provenance for the data pipeline.

        Returns:
            str: Plan provenance string.
        """
        return self.get_data("provenance")

    # plan input / output
    def set_plan_input_id(self, input_id, sync=None):
        """
        Set the plan input node ID for the data pipeline.

        Parameters:
            input_id: Input node ID.
            sync: Synchronization flag.
        """
        self.set_plan_input(input_id, sync=sync)

    def set_plan_input(self, i, sync=None):
        """
        Set the plan input for the data pipeline.

        Parameters:
            i: Input node object, id, or label.
            sync: Synchronization flag.
        """
        input_id = i

        input_node = self.get_node(i)
        # internal node, get node id
        if input_node:
            input_id = input_node.get_id()

        self.set_data("input", input_id, sync=sync)

    def get_plan_input_id(self, pipeline=None):
        """
        Get the plan input ID for the data pipeline.

        Parameters:
            pipeline: Pipeline entity or ID.

        Returns:
            Plan input ID.
        """
        if pipeline is None:
            return self.get_data("input")
        else:
            pipeline_entity = self.get_entity(pipeline)
            return pipeline_entity.get_data("input")

    def get_plan_input(self, pipeline=None):
        """
        Get the plan input node for the data pipeline.

        Parameters:
            pipeline: Pipeline entity or ID.

        Returns:
            Plan input node.
        """
        plan_input_id = self.get_plan_input_id(pipeline=pipeline)
        return self.get_node(plan_input_id)

    def set_plan_output_id(self, output_id, sync=None):
        """
        Set the plan output node ID for the data pipeline.

        Parameters:
            output_id: Output node ID.
            sync: Synchronization flag.
        """
        self.set_plan_output(output_id, sync=sync)

    def set_plan_output(self, o, sync=None):
        """
        Set the plan outputfor the data pipeline.

        Parameters:
            o: Output node object, id, or label.
            sync: Synchronization flag.
        """
        output_id = o

        output_node = self.get_node(o)
        # internal node, get node id
        if output_node:
            output_id = output_node.get_id()

        self.set_data("output", output_id, sync=sync)

    def get_plan_output_id(self, pipeline=None):
        """
        Get the plan output ID for the data pipeline.

        Parameters:
            pipeline: Pipeline entity or ID.

        Returns:
            Plan output ID.
        """
        if pipeline is None:
            return self.get_data("output")
        else:
            pipeline_entity = self.get_entity(pipeline)
            return pipeline_entity.get_data("output")

    def get_plan_output(self, pipeline=None):
        """
        Get the plan output node for the data pipeline.

        Parameters:
            pipeline: Pipeline entity or ID.

        Returns:
            Plan output node.
        """
        plan_output_id = self.get_plan_output_id(pipeline=pipeline)
        return self.get_node(plan_output_id)

    ## nodes
    def set_node_value(self, n, value=None, provenance=None, sync=None):
        """
        Set the node value for a node in the data pipeline.

        Parameters:
            n: Node object, id, or label.
            value: Value to set.
            provenance: Provenance information.
            sync: Synchronization flag.
        """
        node = self.get_node(n)
        node.set_data("value", value, sync=sync)

        if provenance:
            values = node.get_data("values")
            values[provenance] = value

            node.synchronize(key="values." + provenance, value=value, sync=sync)

    def get_node_value(self, n, provenance=None):
        """
        Get the node values for a node in the data pipeline, optionally filtered by provenance.

        Parameters:
            n: Node object, id, or label.
            provenance: Provenance information.

        Returns:
            Node value.
        """
        node = self.get_node(n)
        if provenance:
            values = node.get_data("values")
            if provenance in values:
                return values[provenance]
            else:
                return None
        else:
            return node.get_data("value")

    def get_node_values(self, n):
        """
        Get all node values for a node in the data pipeline.

        Parameters:
            n: Node object, id, or label.

        Returns:
            dict: Dictionary of provenance-value pairs.
        """
        node = self.get_node(n)
        return node.get_data("values")

    def set_node_status(self, n, status=None, provenance=None, sync=None):
        """
        Set the node status for a node in the data pipeline, optionally for specific provenance.

        Parameters:
            n: Node object, id, or label.
            status: Status to set.
            provenance: Provenance information.
            sync: Synchronization flag.
        """
        node = self.get_node(n)
        node.set_data("status", status, sync=sync)

        if provenance:
            statuses = node.get_data("statuses")
            statuses[provenance] = status

            node.synchronize(key="statuses." + provenance, value=status, sync=sync)

    def get_node_status(self, n, provenance=None):
        """
        Get the node status for a node in the data pipeline, optionally filtered by provenance.

        Parameters:
            n: Node object, id, or label.
            provenance: Provenance information.

        Returns:
            Node status.
        """
        node = self.get_node(n)
        if provenance:
            statuses = node.get_data("statuses")
            if provenance in statuses:
                return statuses[provenance]
            else:
                return None
        else:
            return node.get_data("status")

    def get_node_statuses(self, n):
        """
        Get all node statuses for a node in the data pipeline.

        Parameters:
            n: Node object, id, or label.

        Returns:
            dict: Dictionary of provenance-status pairs.
        """
        node = self.get_node(n)
        return node.get_data("statuses")

    def set_node_provenance(self, n):
        """
        Set the node provenance for a node in the data pipeline.

        Parameters:
            n: Node object, id, or label.
        """
        node = self.get_node(n)

        plan_provenance = self.get_plan_provenance()
        node.set_data("provenance", plan_provenance + "." + self.get_id())

    def define_input(self, label=None, value=None, provenance=None, properties={}, sync=None):
        """
        Define an input node in the data pipeline.

        Parameters:
            label: Node label.
            value: Input value.
            provenance: Provenance information.
            properties: Node properties.
            sync: Synchronization flag.
        """
        input_node = self.create_node(label=label, type=str(NodeType.INPUT), properties=properties, sync=sync)

        # values / provenance
        input_node.set_data('values', {}, sync=sync)
        input_node.set_data('statuses', {}, sync=sync)

        # input value/stream
        self.set_node_value(input_node, value=value, provenance=provenance, sync=sync)

        # set provenance
        self.set_node_provenance(input_node)

        return input_node

    def define_output(self, label=None, value=None, provenance=None, properties={}, sync=None):
        """
        Define an output node in the data pipeline.

        Parameters:
            label: Node label.
            value: Output value.
            provenance: Provenance information.
            properties: Node properties.
            sync: Synchronization flag.
        """
        output_node = self.create_node(label=label, type=str(NodeType.OUTPUT), properties=properties, sync=sync)

        # values / provenance
        output_node.set_data('values', {}, sync=sync)
        output_node.set_data('statuses', {}, sync=sync)

        # output value/stream
        self.set_node_value(output_node, value=value, provenance=provenance, sync=sync)

        # set provenance
        self.set_node_provenance(output_node)

        return output_node

    def define_operator(self, name, label=None, attributes={}, properties={}, sync=None):
        """
        Define an operator node in the data pipeline.

        Parameters:
            name: Operator name.
            label: Node label.
            attributes: Node attributes.
            properties: Node properties.
            sync: Synchronization flag.
        """
        # checks
        if name is None:
            raise Exception("Name is not specified")

        operator_node = self.create_node(label=label, type=str(NodeType.OPERATOR), properties=properties, sync=sync)

        # values / provenance
        operator_node.set_data('values', {}, sync=sync)
        operator_node.set_data('statuses', {}, sync=sync)

        operator = self.create_operator(name, attributes=attributes, properties=properties, sync=sync)

        self.set_node_entity(operator_node, operator, sync=sync)

        # set provenance
        self.set_node_provenance(operator_node)

        return operator_node

    ### operator
    def create_operator(self, name, label=None, attributes={}, properties={}, sync=None):
        """
        Create an operator entity.

        Parameters:
            name: Operator name (full path, e.g. /server/<server>/operator/<operator>).
            label: Operator label.
            attributes: Operator attributes.
            properties: Operator properties.
            sync: Synchronization flag.
        """
        operator = self.create_entity(label=label, type=str(EntityType.OPERATOR), properties=properties, sync=sync)
        operator.set_data("name", name)
        operator.set_data("attributes", attributes)

        return operator

    # override merge to set provenance
    # def merge(self, merge_plan, merge_plan_provenance, sync=None):
    #     merge_plan_id = merge_plan.get_id()

    #     merge_plan_nodes = merge_plan.get_nodes()

    #     super().merge(merge_plan, sync=sync)

    #     # set provenance for each node in merged plan
    #     merge_plan.set_data("provenance", merge_plan_provenance)

    #     merge_plan_operator_provenance = merge_plan_provenance + "." + merge_plan_id
    #     for merge_plan_node_id in merge_plan_nodes:
    #         merge_plan_node = self.get_node(merge_plan_node_id)
    #         merge_plan_node.set_data("provenance", merge_plan_operator_provenance, sync=sync)
