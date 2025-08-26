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
Status.RUNNING = Status("REFINED")
Status.PLANNED = Status("EXECUTED")


class NodeType(Constant):
    def __init__(self, c):
        super().__init__(c)


NodeType.INPUT = Constant("INPUT")
NodeType.OUTPUT = Constant("OUTPUT")
NodeType.OPERATOR = Constant("OPERATOR")


class EntityType(Constant):
    def __init__(self, c):
        super().__init__(c)


EntityType.OPERATOR = Constant("OPERATOR")


###############
### DataPipeline
#
class DataPipeline(dag_utils.Plan):
    def __init__(self, id=None, label=None, type="DATA_PIPELINE", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

    # nodes
    def define_input(self, label=None, value=None, stream=None, properties={}, sync=None):
        if label is None:
            raise Exception("Label is not specified")
        input_node = self.create_node(label=label, type=str(NodeType.INPUT), properties=properties, sync=sync)

        # input value/stream
        input_node.set_data('value', value, sync=sync)

        return input_node

    def define_output(self, label=None, value=None, stream=None, properties={}, sync=None):
        if label is None:
            raise Exception("Label is not specified")
        output_node = self.create_node(label=label, type=str(NodeType.OUTPUT), properties=properties, sync=sync)

        # output value/stream
        output_node.set_data('value', value, sync=sync)

        return output_node

    def define_operator(self, name=None, label=None, properties={}, sync=None):
        # checks
        if name is None:
            raise Exception("Name is not specified")
        if label is None:
            label = name

        operator_node = self.create_node(label=label, type=str(NodeType.OPERATOR), properties=properties, sync=sync)

        operator = self.create_operator(properties=properties, sync=sync)
        operator.set_data("name", name)

        self.set_node_entity(operator_node, operator, sync=sync)

        return operator_node

    ### operator
    def create_operator(self, label=None, properties=None, sync=None):
        return self.create_entity(label=label, type=str(EntityType.OPERATOR), properties=properties, sync=sync)

    def execute(self, budget):
        return None
