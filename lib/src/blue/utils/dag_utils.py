###### Parsers, Utils
import json
import logging
import copy

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.session import Session
from blue.stream import Constant, ControlCode, ConstantEncoder
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, json_utils


class Base:
    def __init__(self, name=None, label=None, type=None, path=None, properties=None, synchronizer=None, auto_sync=False):

        # data
        self._init_data()

        # name
        self._set_data("name", name)

        # create unique id
        if id is None:
            id = uuid_utils.create_uuid()
        self._set_data("id", id)

        # label
        if label is None:
            label = name
        self._set_data("label", label)

        # type
        self._set_data("type", type)

        # sync path
        if path is None:
            path = "$"
        self.path = path
        self.auto_sync = auto_sync
        if synchronizer:
            self.synchronizer = synchronizer

        self._initialize(properties=properties)

    def _init_data(self):
        self.__data__ = {}

    def _set_data(self, key, value):
        self.__data__[key] = value

    def _get_data(self, key):
        if key in self.__data__:
            return self.__data__[key]
        else:
            return None

    def _append_data(self, key, value):
        l = self._get_data(key)
        if type(l) is list:
            l.append(value)
        else:
            raise Exception("Data is not a list")

    def _set_data_path(self, path, key, value):
        json_utils.json_query_set(self.__data__, key, value, context=path)

    def _get_data_path(self, path, single=True):
        return json_utils.json_query(self.__data__, path, single=single)

    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

        # save
        if self.auto_sync:
            self.synchronize()

    # basics
    def get_name(self):
        return self._get_data("name")

    def get_id(self):
        return self._get_data("id")

    def get_label(self):
        return self._get_data("label")

    def get_type(self):
        return self._get_data("type")

    # properties
    def _initialize_properties(self):
        self._set_data("properties", {})

    def _update_properties(self, properties=None, sync=False):
        if properties is None:
            return

        # override
        for p in properties:
            self.set_property(p, properties[p], sync=sync)

        if self.auto_sync or sync:
            self.synchronize(self.path + ".properties")

    def set_property(self, key, value, sync=False):
        properties = self.get_properties()
        properties[key] = value

        if self.auto_sync or sync:
            self.synchronize(self.path + ".properties." + key, value)

    def get_property(self, key):
        properties = self.get_properties()
        if key in properties:
            return properties[key]
        return None

    def get_properties(self):
        return self._get_data("properties")

    # sync
    def to_json(self):
        return self.__data__

    def synchronize(self, path, value):
        if self.synchronizer is None:
            raise Exception("No sychronized function set")

        if path is None:
            path = self.path
            value = self.__data__

        self.synchronizer(self.__data__, path, value)


class Node(Base):
    def __init__(self, name, id=None, label=None, type=None, path=None, properties=None, synchronizer=None, auto_sync=False):
        super().__init__(name, id=id, label=label, type=type, path=path, properties=properties, synchronizer=None, auto_sync=False)

    def _init_data(self):
        super._init_data()

        self._set_data("prev", [])
        self._set_data("next", [])

    def add_next(self, t_id, sync=False):
        self._append_data("next", t_id)
        if self.auto_sync or sync:
            self.synchronize(self.path + ".next")

    def add_prev(self, f_id, sync=False):
        self._append_data("prev", f_id)
        if self.auto_sync or sync:
            self.synchronize(self.path + ".prev")

    def add_next_node(self, t, sync=False):
        t_id = t.get_id()
        self.add_next(t_id, sync=sync)

    def add_prev_node(self, f, sync=False):
        f_id = f.get_id()
        self.add_prev(f_id, sync=sync)


class Entity(Base):
    def __init__(self, name, id=None, label=None, type="Entity", path=None, properties=None, synchronizer=None, auto_sync=False):
        super().__init__(name, id=id, label=label, type=type, path=path, properties=properties, synchronizer=None, auto_sync=False)


class DAG(Base):
    def __init__(self, name, id=None, label=None, type="DAG", path=None, properties=None, synchronizer=None, auto_sync=False):
        super().__init__(name, id=id, label=label, type=type, path=path, properties=properties, synchronizer=None, auto_sync=False)

    def _init_data(self):
        super._init_data()

        self.set_data("nodes", {})
        self.set_data("map", {})

    def _verify_node(self, name, id=None, label=None, type=None, path=None, properties=None):
        # check if label is unique
        if label and self.get_node_by_label(label):
            return False
        return True

    def create_node(self, name, id=None, label=None, type=None, path=None, properties=None, synchronizer=None, auto_sync=False):
        # verify node, first
        if self.verify_node(name, id=id, label=label, type=type, properties=properties):
            raise Exception("Cannot create node due to failed varification")

        # create node
        node = Node(name, id=id, label=label, type=type, path=path, properties=properties, synchronizer=synchronizer, auto_sync=auto_sync)
        node_id = node.get_id()
        node_label = node.get_label()

        # add to nodes
        nodes = self.get_nodes()
        nodes[node_id] = node

        # add to map
        map = self._get_data("map")
        map[node_label] = node_id

        return node

    def get_nodes(self):
        return self._get_data("nodes")

    def get_node(self, n):
        node = self.get_node_by_id(n)
        if node is None:
            node = self.get_node_by_label(n)
        return node

    def get_node_by_id(self, node_id):
        nodes = self.get_nodes()
        if node_id in nodes:
            return nodes[node_id]
        else:
            return None

    def get_node_by_label(self, node_label):
        map = self._get_data("map")
        node = None
        if node_label in map:
            node_id = map[node_label]
            node = self.get_node_by_id(node_id)
        return node

    def filter_nodes(self):
        pass

    def connect_nodes(self, f, t):
        pass
