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

    def append_data(self, key, value, unique=False, sync=None):
        l = self.get_data(key)
        if isinstance(l, list):
            if unique:
                if value in l:
                    return
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
        self.append_data("next", t_id, unique=True)

        self.synchronize(key="next", single=False, sync=sync)

    def _add_prev(self, f_id, sync=None):
        self.append_data("prev", f_id, unique=True)

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

    def create_node(self, id=None, label=None, type=None, properties=None, sync=None):
        # verify node, first
        if not self._verify_node(label=label, type=type, properties=properties):
            raise Exception("Cannot create node due to failed varification")

        # create node
        node = Node(id=id, label=label, type=type, properties=properties, path=self.path + "." + self.get_id() + ".nodes", synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=sync)
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
        if cls is None:
            cls = Node

        if isinstance(n, cls):
            return n
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

    def get_prev_nodes(self, n):
        node = self.get_node(n)
        prev_nodes = []
        if node:
            prev_ids = node.get_data('prev')
            for prev_id in prev_ids:
                prev_node = self.get_node_by_id(prev_id)
                if prev_node:
                    prev_nodes.append(prev_node)

        return prev_nodes

    def get_next_nodes(self, n):
        node = self.get_node(n)
        next_nodes = []
        if node:
            next_ids = node.get_data('next')
            for next_id in next_ids:
                next_node = self.get_node_by_id(next_id)
                if next_node:
                    next_nodes.append(next_node)

        return next_nodes

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


class EntityDAG(DAG):
    def __init__(self, id=None, label=None, type="DAG", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

    def _init_data(self, sync=None):
        super()._init_data(sync=sync)

        self.set_data("entities", {}, sync=sync)

    def verify_entity(self, label=None, type=None, properties=None):
        # verify if label is unique
        if label and self.is_mapped(label):
            return False

        return True

    def create_entity(self, id=None, label=None, type=None, properties=None, sync=None):
        # verify entity
        if not self.verify_entity(label=label, type=type, properties=properties):
            raise Exception("Cannot create entity due to failed varification")

        # check type, add if necessary
        if not self.has_entity_type(type):
            self.add_entity_type(type, sync=sync)

        # create entity
        entity = Entity(
            id=id,
            label=label,
            type=type,
            properties=properties,
            path=self.path + "." + self.get_id() + ".entities." + type,
            synchronizer=self.synchronizer,
            auto_sync=self.auto_sync,
            sync=sync,
        )
        entity_id = entity.get_id()
        entity_label = entity.get_label()

        entities = self.get_entities(type=type)
        entities[entity_id] = entity.get_data()

        # set nodes
        entity.set_data("nodes", [])

        # add to map
        if label:
            self.map(entity_label, entity_id, sync=sync)

        return entity

    def has_entity_type(self, type):
        entities = self.get_data("entities")
        return type in entities

    def add_entity_type(self, type, sync=None):
        entities = self.get_data("entities")
        if type in entities:
            return
        entities[type] = {}

        self.synchronize(key="entities." + type, value=entities[type], sync=sync)

    def get_entities(self, type=None):
        entities = self.get_data("entities")
        if type and type in entities:
            return entities[type]
        return entities

    def get_entity(self, e, type=None, cls=None):
        if cls is None:
            cls = Entity

        if isinstance(e, cls):
            return e

        entity = self.get_entity_by_id(e, type=type, cls=cls)
        if entity is None:
            entity = self.get_entity_by_label(e, type=type, cls=cls)
        return entity

    def get_entity_by_id(self, entity_id, type=None, cls=None):
        entities = self.get_entities(type=type)

        entity_data = None
        if type:
            if entity_id in entities:
                entity_data = entities[entity_id]
        else:
            for type in entities:
                if entity_id in entities[type]:
                    entity_data = entities[type][entity_id]

        if entity_data:
            if cls is None:
                cls = Entity
            return cls.from_dict(entity_data, path=self.path + "." + self.get_id() + ".entities." + type, synchronizer=self.synchronizer, auto_sync=self.auto_sync, sync=False)
        else:
            return None

    def get_entity_by_label(self, entity_label, type=None, cls=None):
        map = self.get_data("map")
        entity = None
        if entity_label in map:
            entity_id = map[entity_label]
            entity = self.get_entity_by_id(entity_id, type=type, cls=cls)
        return entity

    def get_nodes_by_entity(self, e, type=None, cls=None, node_type=None):
        entity = self.get_entity(e, type=type, cls=cls)
        if entity is None:
            return []
        nodes = []

        ids = entity.get_data("nodes")
        for id in ids:
            node = self.get_node(id)
            if node_type:
                if isinstance(node_type, list):
                    if node.get_type() in node_type:
                        nodes.append(node)
                else:
                    if node.get_type() == node_type:
                        nodes.append(node)
            else:
                nodes.append(node)
        return nodes

    def set_node_entity(self, n, e, field=None, sync=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Entity for non-existing node cannot be set")

        node_id = node.get_id()

        entity = None
        if e is None:
            if field is None:
                field = "Entity"
            node.set_data(field, None, sync=sync)
        else:
            entity = self.get_entity(e)
            if field is None:
                field = entity.get_type()
            if field is None:
                field = "Entity"

            if entity:
                entity.append_data("nodes", node_id, sync=sync)
                node.set_data(field, entity.get_id(), sync=sync)

    def get_node_entity(self, n, type=None, cls=None, field=None):
        node = self.get_node(n)
        if node is None:
            raise Exception("Entity for non-existing node cannot be get")

        if field is None:
            field = type
        if field is None:
            field = "Entity"

        entity_id = node.get_data(field)
        return self.get_entity(entity_id, type=type, cls=cls)

    @classmethod
    def _validate(cls, d):
        dv = super(EntityDAG, cls)._validate(d)
        if dv is None:
            return None

        if 'entities' not in dv:
            dv['entities'] = {}

        return dv


class Plan(EntityDAG):
    def __init__(self, id=None, label=None, type="PLAN", properties=None, path=None, synchronizer=None, auto_sync=False, sync=None):
        super().__init__(id=id, label=label, type=type, properties=properties, path=path, synchronizer=synchronizer, auto_sync=auto_sync, sync=sync)

    def merge(self, merge_plan, sync=None):
        nodes = self.get_nodes()
        entities = self.get_entities()

        ### extract from merge plan
        merge_plan_id = merge_plan.get_id()
        merge_plan_nodes = merge_plan.get_nodes()
        merge_plan_entities = merge_plan.get_entities()
        merge_plan_map = merge_plan.get_data("map")
        merge_plan_data = merge_plan.get_data()

        ### inject merge_plan as entity
        merge_plan_entity = self.create_entity(id=merge_plan.get_id(), label=merge_plan.get_label(), type=merge_plan.get_type(), properties=merge_plan.get_properties(), sync=sync)

        # copy over data
        for key in merge_plan_data:
            if key not in ["entities", "map", "properties", "id", "label", "type", "nodes"]:
                merge_plan_entity.set_data(key, merge_plan_data[key])

        e = self.get_entity(merge_plan_id)

        ### merge nodes
        merge_plan_nodes = merge_plan.get_nodes()
        for merge_plan_node_id in merge_plan_nodes:
            merge_plan_node_data = merge_plan_nodes[merge_plan_node_id]

            merge_plan_node_label = merge_plan_node_data['label']
            nodes[merge_plan_node_id] = merge_plan_node_data

            # sync
            self.synchronize(key="nodes." + merge_plan_node_id, value=merge_plan_node_data, sync=sync)

            # add plan entity
            self.set_node_entity(merge_plan_node_id, merge_plan_id, sync=sync)

            # add to map
            if merge_plan_node_label:
                self.map(merge_plan_node_label, merge_plan_node_id, sync=sync)

        ### merge entities
        for merge_plan_entity_type in merge_plan_entities:
            if not merge_plan_entity_type in entities:
                self.add_entity_type(merge_plan_entity_type, sync=sync)

            for merge_plan_entity_id in merge_plan_entities[merge_plan_entity_type]:
                merge_plan_entity = merge_plan.get_entity(merge_plan_entity_id, type=merge_plan_entity_type)
                merge_plan_entity_label = merge_plan_entity.get_label()

                entities[merge_plan_entity_type][merge_plan_entity_id] = merge_plan_entities[merge_plan_entity_type][merge_plan_entity_id]

                # add to map
                if merge_plan_entity_label:
                    self.map(merge_plan_entity_label, merge_plan_entity_id, sync=sync)
