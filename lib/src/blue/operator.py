###### Parsers, Formats, Utils
import time
import math
import logging
import time
import json


###### Blue
from blue.stream import Message, MessageType, ContentType, ControlCode
from blue.connection import PooledConnectionFactory
from blue.pubsub import Consumer, Producer
from blue.registry import Registry
from blue.utils import json_utils, uuid_utils


###############
### OperatorRegistry
#
class OperatorRegistry(Registry):
    def __init__(self, name="OPERATOR_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, type="operator", id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization

    def _initialize_properties(self):
        super()._initialize_properties()

    ######### operator
    def add_operator(self, operator, created_by, description="", properties={}, rebuild=False):
        super().register_record(operator, "operator", "/", created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_operator(self, operator, description="", icon=None, properties={}, rebuild=False):
        super().update_record(operator, "operator", "/", description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_operator(self, operator, rebuild=False):
        record = self.get_operator(operator)
        super().deregister(record, rebuild=rebuild)

    def get_operator(self, operator):
        return super().get_record(operator, 'operator', '/')

    def get_operator_description(self, operator):
        return super().get_record_description(operator, 'operator', '/')

    def set_operator_description(self, operator, description, rebuild=False):
        super().set_record_description(operator, 'operator', '/', description, rebuild=rebuild)

    # operator properties
    def get_operator_properties(self, operator):
        return super().get_record_properties(operator, 'operator', '/')

    def get_operator_property(self, operator, key):
        return super().get_record_property(operator, 'operator', '/', key)

    def set_operator_property(self, operator, key, value, rebuild=False):
        super().set_record_property(operator, 'operator', '/', key, value, rebuild=rebuild)

    def delete_operator_property(self, operator, key, rebuild=False):
        super().delete_record_property(operator, 'operator', '/', key, rebuild=rebuild)

    # operator image (part of properties)
    def get_operator_image(self, operator):
        return self.get_operator_property(operator, 'image')

    def set_operator_image(self, operator, image, rebuild=False):
        self.set_operator_property(operator, 'image', image, rebuild=rebuild)
