###### Parsers, Utils
import json
import logging
import copy

###### Blue
from blue.utils import uuid_utils, json_utils


###############
### Base
#
# a base entity with a label, type and set of properties
#
# if auto_sync=True, synchronize all updates, expect for specific updates where sync=True
# if sync=True, synchronize even if auto_sync=False
# where path is context to synchronize object
#
# sync | auto_sync |  synchronize?
# --------------------------
# NS     T            T
# NS     F            F
# F      F            F
# F      T            F
# T      F            T
# T      T            T
class Base:
    def __init__(self, id=None, label=None, type=None, properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):

        # create unique id
        if id is None:
            id = uuid_utils.create_uuid()
        self.id = id

        # sync
        if path is None:
            path = "$"
        self.path = path

        self.auto_sync = auto_sync
        if synchronizer:
            self.synchronizer = synchronizer

        # data
        self.__data__ = {}
        self.synchronize(sync=sync)

        self.set_data("id", id, sync=sync)

        # label, optional, unique
        self.set_data("label", label, sync=sync)

        # type
        self.set_data("type", type, sync=sync)

        self._initialize(properties=properties, sync=sync)

    def _init_data(self, sync=None):
        pass

    def set_data(self, key, value, sync=None):
        self.__data__[key] = value

        # sync
        self.synchronize(key=key, value=value, sync=sync)

    def get_data(self, key=None):
        if key is None:
            return self.__data__
        elif key in self.__data__:
            return self.__data__[key]
        else:
            return None

    def append_data(self, key, value, sync=None):
        l = self.get_data(key)
        if type(l) is list:
            l.append(value)

            # sync
            self.synchronize(key=key, single=False, sync=sync)
        else:
            raise Exception("Data is not a list")

    def _initialize(self, properties=None, sync=None):
        self._init_data(sync=sync)
        self._initialize_properties(sync=sync)
        self._update_properties(properties=properties, sync=sync)

    # basics
    def get_id(self):
        return self.get_data("id")

    def get_label(self):
        return self.get_data("label")

    def get_type(self):
        return self.get_data("type")

    # properties
    def _initialize_properties(self, sync=None):
        self.set_data("properties", {}, sync=sync)

    def _update_properties(self, properties=None, sync=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.set_property(p, properties[p], sync=sync)

    def set_property(self, key, value, sync=None):
        properties = self.get_properties()
        properties[key] = value

        self.synchronize(key="properties." + key, value=value)

    def get_property(self, key):
        properties = self.get_properties()
        if key in properties:
            return properties[key]
        return None

    def get_properties(self):
        return self.get_data("properties")

    # sync
    def to_dict(self):
        return self.__data__

    @classmethod
    def _validate(cls, d):
        if 'id' not in d:
            return None
        if 'type' not in d:
            return None
        if 'label' not in d:
            d['label'] = None
        if 'properties' not in d:
            d['properties'] = {}
        return d

    @classmethod
    def from_dict(cls, d, path=None, synchronizer=None, auto_sync=False, sync=None):
        d = cls._validate(d)
        if d:
            id = d['id']
            b = cls(id=id, path=path, synchronizer=synchronizer, auto_sync=False, sync=False)

            # hard-set data
            b.__data__ = d
            b.auto_sync = auto_sync

            b.synchronize(sync=sync)
            return b
        else:
            raise Exception("Failed validation")

    def synchronize(self, key=None, value=None, single=True, sync=None):
        # sync is not set
        if sync is None:
            # auto sync is off -> do not sync
            if self.auto_sync == False:
                return

        # sync is False, -> do not sync
        if sync == False:
            return

        if self.synchronizer is None:
            raise Exception("No sychronizer set")

        # entire object
        if key is None:
            value = self.__data__
        elif value is None:
            # query value
            value = json_utils.json_query(self.__data__, "$." + key, single=single)

        context = self.path
        if key is None:
            self.synchronizer(context, self.id, value)
        else:
            self.synchronizer(context + "." + self.id, key, value)

    def synchronizer(self, path, key, value):
        print("synchronize: " + str(path) + "." + (str(key) if key else "NONE") + "=" + json.dumps(value))


class Node(Base):
    def __init__(self, id=None, label=None, type=None, properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

    def _init_data(self, sync=None):
        super()._init_data(sync=sync)

        self.set_data("prev", [], sync=sync)
        self.set_data("next", [], sync=sync)

    def _add_next(self, t_id, sync=None):
        self.append_data("next", t_id)

        self.synchronize(key="next", single=False, sync=sync)

    def _add_prev(self, f_id, sync=None):
        self.append_data("prev", f_id)

        self.synchronize(key="prev", single=False, sync=sync)

    def connect_to(self, t, sync=None):
        # add next
        t_id = t.get_id()
        self._add_next(t_id, sync=sync)
        # add prev
        t._add_prev(self.get_id(), sync=sync)

    @classmethod
    def _validate(cls, d):
        dv = super(Node, cls)._validate(d)
        if dv is None:
            return None

        if 'prev' not in dv:
            dv['prev'] = []
        if 'next' not in dv:
            dv['next'] = []

        return dv


###############
### Entity
#
class Entity(Base):
    def __init__(self, id=None, label=None, type="Entity", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)


###############
### DAG
#
class DAG(Base):
    def __init__(self, id=None, label=None, type="DAG", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

    def _init_data(self, sync=None):
        super()._init_data(sync=sync)

        self.set_data("nodes", {}, sync=sync)
        self.set_data("map", {}, sync=sync)

    def _verify_node(self, label=None, type=None, properties=None):
        # verify if label is unique
        if label and self.get_node_by_label(label):
            return False
        return True

    def create_node(self, label=None, type=None, properties=None, sync=None):
        # verify node, first
        if not self._verify_node(label=label, type=type, properties=properties):
            raise Exception("Cannot create node due to failed varification")

        # create node
        node = Node(label=label, type=type, properties=properties, path=self.path + "." + self.get_id() + ".nodes", synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=sync)
        node_id = node.get_id()
        node_label = node.get_label()

        # add to nodes
        nodes = self.get_nodes()
        nodes[node_id] = node.get_data()

        # add to map
        if label:
            self.map(node_label, node_id, sync=sync)

        return node

    def connect_nodes(self, f, t, sync=None):
        if isinstance(f, Node):
            f_node = f
        else:
            f_node = self.get_node(f)
        if f_node is None:
            raise Exception("Undefined from node")

        if isinstance(t, Node):
            t_node = t
        else:
            t_node = self.get_node(t)
        if t_node is None:
            raise Exception("Undefined to node")

        f_node.connect_to(t_node, sync=sync)

    def get_nodes(self):
        return self.get_data("nodes")

    def get_node(self, n, cls=None):
        node = self.get_node_by_id(n, cls=cls)
        if node is None:
            node = self.get_node_by_label(n, cls=cls)
        return node

    def get_node_by_id(self, node_id, cls=None):
        nodes = self.get_nodes()
        if node_id in nodes:
            node_data = nodes[node_id]
            if cls is None:
                cls = Node
            return cls.from_dict(node_data, path=self.path + "." + self.get_id() + ".nodes", synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=False)
        else:
            return None

    def get_node_by_label(self, node_label, cls=None):
        map = self.get_data("map")
        node = None
        if node_label in map:
            node_id = map[node_label]
            node = self.get_node_by_id(node_id)
        return node

    def filter_nodes(self, filter_node_type=None, filter_hasPrev=None, filter_hasNext=None):
        filtered_nodes = {}

        for node_id in self.get_nodes():
            node = self.get_node(node_id)
            node_type = node.get_data("type")
            prev = node.get_data("prev")
            next = node.get_data("next")

            if filter_node_type:
                if node_type not in filter_node_type:
                    continue

            if filter_hasPrev:
                if len(prev) == 0:
                    continue

            if filter_hasNext:
                if len(next) == 0:
                    continue

            filtered_nodes[node_id] = node

        return filtered_nodes

    def count_nodes(self, filter_node_type=None, filter_hasPrev=None, filter_hasNext=None):
        nodes = self.filter_nodes(filter_node_type=filter_node_type, filter_hasPrev=filter_hasPrev, filter_hasNext=filter_hasNext)
        return len(nodes)

    def is_node_leaf(self, n):
        node = self.get_node(n)
        prev = node.get_data("prev")
        next = node.get_data("next")

        if len(prev) > 0 and len(next) == 0:
            return True
        else:
            return False

    def map(self, f, t, sync=None):
        map = self.get_data("map")
        map[f] = t

        self.synchronize(key="map." + f, value=t, sync=sync)

    def is_mapped(self, i):
        map = self.get_data("map")
        if i in map:
            return True
        else:
            return False

    @classmethod
    def _validate(cls, d):
        dv = super(DAG, cls)._validate(d)
        if dv is None:
            return None

        if 'nodes' not in dv:
            dv['nodes'] = {}
        if 'map' not in dv:
            dv['map'] = {}

        return dv
