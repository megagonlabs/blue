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
    def __init__(self, id=None, label=None, type="DATA_PIPELINE", properties=None, attributes=None, path=None, plan_input=None, plan_output=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

        # set plan input / output
        self.set_plan_input(plan_input, sync=sync)
        self.set_plan_output(plan_output), sync=sync

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

    # nodes
    def define_input(self, label=None, value=None, properties={}, sync=None):
        input_node = self.create_node(label=label, type=str(NodeType.INPUT), properties=properties, sync=sync)

        # input value/stream
        input_node.set_data('value', value, sync=sync)

        return input_node

    def define_output(self, label=None, value=None, properties={}, sync=None):
        output_node = self.create_node(label=label, type=str(NodeType.OUTPUT), properties=properties, sync=sync)

        # output value/stream
        output_node.set_data('value', value, sync=sync)

        return output_node

    def define_operator(self, name, label=None, attributes={}, properties={}, sync=None):
        # checks
        if name is None:
            raise Exception("Name is not specified")

        operator_node = self.create_node(label=label, type=str(NodeType.OPERATOR), properties=properties, sync=sync)

        operator = self.create_operator(name, attributes=attributes, properties=properties, sync=sync)

        self.set_node_entity(operator_node, operator, sync=sync)

        return operator_node

    ### operator
    def create_operator(self, name, label=None, attributes={}, properties={}, sync=None):
        operator = self.create_entity(label=label, type=str(EntityType.OPERATOR), properties=properties, sync=sync)
        operator.set_data("name", name)
        operator.set_data("attributes", attributes)

        return operator

    def execute(self, budget):
        return None
