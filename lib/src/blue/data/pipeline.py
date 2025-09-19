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
    def __init__(self, c):
        super().__init__(c)


NodeType.INPUT = NodeType("INPUT")
NodeType.OUTPUT = NodeType("OUTPUT")
NodeType.OPERATOR = NodeType("OPERATOR")


class EntityType(Constant):
    def __init__(self, c):
        super().__init__(c)


EntityType.OPERATOR = EntityType("OPERATOR")
EntityType.DATA_PIPELINE = EntityType("DATA_PIPELINE")


###############
### DataPipeline
#
class DataPipeline(dag_utils.Plan):
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
        self.set_data("attributes", {}, sync=sync)

    def _update_attributes(self, attributes=None, sync=None):
        if attributes is None:
            return

        # override
        for a in attributes:
            self.set_attribute(a, attributes[a], sync=sync)

    def set_attribute(self, key, value, sync=None):
        attributes = self.get_attributes()
        attributes[key] = value

        self.synchronize(key="attributes." + key, value=value)

    def get_attribute(self, key):
        attributes = self.get_attributes()
        if key in attributes:
            return attributes[key]
        return None

    def get_attributes(self):
        return self.get_data("attributes")

    # provenance
    def set_plan_provenance(self, plan_provenance, sync=None):
        self.set_data("provenance", plan_provenance, sync=sync)

    def get_plan_provenance(self):
        return self.get_data("provenance")

    # plan input / output
    def set_plan_input_id(self, input_id, sync=None):
        self.set_plan_input(input_id, sync=sync)

    def set_plan_input(self, i, sync=None):
        input_id = i

        input_node = self.get_node(i)
        # internal node, get node id
        if input_node:
            input_id = input_node.get_id()

        self.set_data("input", input_id, sync=sync)

    def get_plan_input_id(self):
        return self.get_data("input")

    def set_plan_output_id(self, output_id, sync=None):
        self.set_plan_output(output_id, sync=sync)

    def set_plan_output(self, o, sync=None):
        output_id = o

        output_node = self.get_node(o)
        # internal node, get node id
        if output_node:
            output_id = output_node.get_id()

        self.set_data("output", output_id, sync=sync)

    def get_plan_output_id(self):
        return self.get_data("output")

    ## nodes
    def set_node_value(self, n, value=None, provenance=None, sync=None):
        node = self.get_node(n)
        node.set_data("value", value, sync=sync)

        if provenance:
            values = node.get_data("values")
            values[provenance] = value

            node.synchronize(key="values." + provenance, value=value, sync=sync)

    def get_node_value(self, n, provenance=None):
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
        node = self.get_node(n)
        return node.get_data("values")

    def get_node_provenance(self, n):
        node = self.get_node(n)

        plan_provenance = self.get_plan_provenance()
        node.set_data("provenance", plan_provenance + "." + plan.get_id())

    def define_input(self, label=None, value=None, provenance=None, properties={}, sync=None):
        input_node = self.create_node(label=label, type=str(NodeType.INPUT), properties=properties, sync=sync)

        # values / provenance
        input_node.set_data('values', {}, sync=sync)

        # input value/stream
        self.set_node_value(input_node, value=value, provenance=provenance, sync=sync)

        # set provenance
        self.set_node_provenance(input_node)

        return input_node

    def define_output(self, label=None, value=None, provenance=None, properties={}, sync=None):
        output_node = self.create_node(label=label, type=str(NodeType.OUTPUT), properties=properties, sync=sync)

        # values / provenance
        output_node.set_data('values', {}, sync=sync)

        # output value/stream
        self.set_node_value(output_node, value=value, provenance=provenance, sync=sync)

        # set provenance
        self.set_node_provenance(input_node)

        return output_node

    def define_operator(self, name, label=None, attributes={}, properties={}, sync=None):
        # checks
        if name is None:
            raise Exception("Name is not specified")

        operator_node = self.create_node(label=label, type=str(NodeType.OPERATOR), properties=properties, sync=sync)

        # values / provenance
        operator_node.set_data('values', {}, sync=sync)

        operator = self.create_operator(name, attributes=attributes, properties=properties, sync=sync)

        self.set_node_entity(operator_node, operator, sync=sync)

        # set provenance
        self.set_node_provenance(input_node)

        return operator_node

    ### operator
    def create_operator(self, name, label=None, attributes={}, properties={}, sync=None):
        operator = self.create_entity(label=label, type=str(EntityType.OPERATOR), properties=properties, sync=sync)
        operator.set_data("name", name)
        operator.set_data("attributes", attributes)

        return operator

    # override merge to set provenance
    def merge(self, merge_plan, sync=None):
        merge_plan_id = merge_plan.get_id()

        merge_plan_nodes = merge_plan.get_nodes()

        super().merge(merge_plan, sync=sync)

        # set provenance for each node in merged plan
        merge_plan_provenance = self.get_plan_provenance() + "." + self.get_id()
        merge_plan.set_data("provenance", merge_plan_provenance)

        merge_plan_operator_provenance = merge_plan_provenance + "." + merge_plan_id
        for merge_plan_node_id in merge_plan_nodes:
            merge_plan_node = self.get_node(merge_plan_node_id)
            merge_plan_node.set_data("provenance", merge_plan_operator_provenance, sync=sync)
