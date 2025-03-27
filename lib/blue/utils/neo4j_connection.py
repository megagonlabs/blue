# neo4j
import neo4j
import copy

from time import sleep

import logging
import traceback

# json utils
from blue.utils import json_utils


def _safe_neo4j_attribute_value(val):
    if val is None:
        return '"none"'
    elif type(val) is str:
        return '"' + val + '"'
    else:
        return str(val)

class NEO4J_Connection:
    def __init__(self, server_url, user, pwd, num_tries=5, try_delay=20):
        self.server_url = server_url

        # Create logger
        self.logger = logging.getLogger('neo4j_connection')
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
        if not len(self.logger.handlers):
            self.logger.addHandler(handler)

        last_exception = None
        for i in range(num_tries):
            try:
                self.neo4j_db = neo4j.GraphDatabase.driver(server_url, auth=(user, pwd))
            except Exception as exception:
                self.logger.error('Connection to neo4j failed: {}'.format(exception))
                traceback.print_exc()
                last_exception = exception
                self.logger.error('Will try again...')
                sleep(try_delay)
                self.logger.error('Failed to connect to to neo4j client. Trying again ({}/{})'.format(i+1,num_tries))
                continue
            else:
                break
        else:
            self.logger.error('Failed to connect to to neo4j. Giving up!!!')
            raise last_exception

    ### helper functions
    def create_node(self, type, attributes, flatten=True, flattenList=True, agent_uuid=None):
        if flatten:
            attributes = json_utils.flatten_json(attributes, flattenList=flattenList)
        with self.neo4j_db.session() as session:
            node = session.write_transaction(self._create_node, type, attributes, agent_uuid)

        if node is None:
            return None
        return self._node_toJSON(node)

    def _create_node(self, tx, t, d, agent_uuid=None):
        result = tx.run(' CREATE (n: ' + t + ') ' +
                        ' '.join([ 'SET n.' + str(key) + ' = ' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' ' +
                        ' SET n._created_on = datetime() ' +
                        ' SET n._modified_on = datetime() ' +
                        ('' if agent_uuid  is None else (' SET n._created_by = "' + agent_uuid + '"' + ' SET n._modified_by = "' + agent_uuid + '" ')) +
                        ' RETURN n ')
        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            return node
        return None




    def delete_node(self, uuid):
        with self.neo4j_db.session() as session:
            session.write_transaction(self._delete_node, uuid)

    def _delete_node(self, tx, uuid):
        result = tx.run(' MATCH (n {uuid: "' + uuid + '"}) '  +
                        ' DETACH DELETE n ')
        return

    def set_node_attributes(self, uuid, attributes, flatten=True, flattenList=True, agent_uuid=None):
        if flatten:
            attributes = json_utils.flatten_json(attributes, flattenList=flattenList)
        with self.neo4j_db.session() as session:
            node = session.write_transaction(self._set_node_attributes, uuid, attributes, agent_uuid)

        if node is None:
            return None
        return self._node_toJSON(node)

    def _set_node_attributes(self, tx, uuid, d, agent_uuid=None):
        result = tx.run(' MATCH (n {uuid:"' + uuid + '"}) '  +
                        ' '.join([ 'SET n.' + str(key) + ' = ' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' ' +
                        ' SET n._modified_on = datetime() ' +
                        ('' if agent_uuid  is None else (' SET n._modified_by = "' + agent_uuid + '" ')) +
                        ' RETURN n')
        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            return node
        return None

    def set_node_attribute(self, uuid, attribute, value, agent_uuid=None):
        d = {}
        d[attribute] = value
        return self.set_node_attributes(uuid, d, agent_uuid)


    def incr_node_attributes(self, uuid, attributes, flatten=True, flattenList=True, agent_uuid=None):
        if flatten:
            attributes = json_utils.flatten_json(attributes, flattenList=flattenList)
        with self.neo4j_db.session() as session:
            node = session.write_transaction(self._incr_node_attributes, uuid, attributes, agent_uuid)

        if node is None:
            return None
        return self._node_toJSON(node)

    def _incr_node_attributes(self, tx, uuid, d, agent_uuid=None):
        result = tx.run(' MATCH(n {uuid:"' + uuid + '"}) '  +
                        ' '.join([ 'SET (CASE WHEN EXISTS(n.' + str(key) + ') THEN n END ).' + str(key) + ' = n.' + str(key) + ' + ' + ( _safe_neo4j_attribute_value(d[key]) ) + ' SET (CASE WHEN NOT EXISTS(n.' + str(key) + ') THEN n END ).' + str(key) + ' = ' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' ' +
                        ' SET n._modified_on = datetime() ' +
                        ('' if agent_uuid  is None else (' SET n._modified_by = "' + agent_uuid + '" ')) +
                        ' RETURN n')

        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            return node
        return None

    def incr_node_attribute(self, uuid, attribute, value, agent_uuid=None):
        d = {}
        d[attribute] = value
        return self.incr_node_attributes(uuid, d, agent_uuid)

    def decr_node_attributes(self, uuid, attributes, flatten=True, flattenList=True, agent_uuid=None):
        if flatten:
            attributes = json_utils.flatten_json(attributes, flattenList=flattenList)
        with self.neo4j_db.session() as session:
            node = session.write_transaction(self._decr_node_attributes, uuid, attributes, agent_uuid)

        if node is None:
            return None
        return self._node_toJSON(node)

    def _decr_node_attributes(self, tx, uuid, d, agent_uuid=None):
        result = tx.run(' MATCH(n {uuid:"' + uuid + '"}) '  +
                        ' '.join([ 'SET (CASE WHEN EXISTS(n.' + str(key) + ') THEN n END ).' + str(key) + ' = n.' + str(key) + ' - ' + ( _safe_neo4j_attribute_value(d[key]) ) + ' SET (CASE WHEN NOT EXISTS(n.' + str(key) + ') THEN n END ).' + str(key) + ' = ' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' ' +
                        ' SET n._modified_on = datetime() ' +
                        ('' if agent_uuid  is None else (' SET n._modified_by = "' + agent_uuid + '" ')) +
                        ' RETURN n')

        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            return node
        return None

    def decr_node_attribute(self, uuid, attribute, value, agent_uuid=None):
        d = {}
        d[attribute] = value
        return self.incr_node_attributes(uuid, d, agent_uuid)



    def set_node_state(self, uuid, state, agent_uuid=None):
        return self.set_node_attribute(uuid, 'state', state, agent_uuid)

    def has_node(self, uuid):
        return self.get_node(uuid) is not None



    def get_node(self, uuid):
        with self.neo4j_db.session() as session:
            node = session.read_transaction(self._get_node, uuid)

        if node is None:
            return None
        return self._node_toJSON(node)

    def _get_node(self, tx, uuid):
        result = tx.run(' MATCH (n {uuid: "' + uuid + '"}) '  +
                        ' RETURN n')
        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            return node
        return None

    def has_node_type(self, uuid, type):
        attributes = {}
        attributes['uuid'] = uuid
        nodes = self.get_nodes_by_label_attributes(attributes, label=type, single=True)
        return len(nodes) > 0

    def has_node_type_creator(self, uuid, type, agent_uuid):
        attributes = {}
        attributes['uuid'] = uuid
        attributes['_created_by'] = agent_uuid
        nodes = self.get_nodes_by_label_attributes(attributes, label=type)
        return len(nodes) > 0

    def has_node_type_attributes(self, uuid, type, attributes):
        attributes['uuid'] = uuid
        nodes = self.get_nodes_by_label_attributes(attributes, label=type)
        return len(nodes) > 0

    def get_nodes_by_type(self, type, skip=None, limit=None, order_by=None, order_dir='ASC'):
        attributes = {}
        nodes = self.get_nodes_by_label_attributes(attributes, label=type, skip=skip, limit=limit, order_by=order_by, order_dir=order_dir)
        return nodes

    def get_nodes_by_type_name(self, type, name, single=False, skip=None, limit=None):
        attributes = {}
        attributes['name'] = name
        nodes = self.get_nodes_by_label_attributes(attributes, label=type, single=single, skip=skip, limit=limit)
        return nodes

    def get_nodes_by_type_creator(self, type, agent_uuid, single=False, skip=None, limit=None):
        attributes = {}
        attributes['_created_by'] = agent_uuid
        nodes = self.get_nodes_by_label_attributes(attributes, label=type, single=single, skip=skip, limit=limit)
        return nodes

    def get_nodes_by_label_attributes(self, attributes, label=None, single=False, skip=None, limit=None, order_by=None, order_dir='ASC'):
        with self.neo4j_db.session() as session:
            nodes = session.read_transaction(self._get_node_by_label_attributes, attributes, label, skip, limit, order_by, order_dir)

        if single:
            if len(nodes) > 0:
                node = nodes[0]
                return self._node_toJSON(node)
            else:
                return None
        else:
            results = []
            for node in nodes:
                results.append(self._node_toJSON(node))
            return results

    def _get_node_by_label_attributes(self, tx, d, label, skip, limit, order_by, order_dir):
        result = tx.run((' MATCH (n {' if label is None else ( 'MATCH (n: ' + label + ' {' )) +
                        ', '.join([ str(key) + ':' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' }) ' +
                        ' RETURN n ' +
                        ( '' if order_by is None else ' ORDER BY ' + 'n.' + str(order_by) + ' ' + ('' if order_dir == 'ASC' else 'DESC' + ' ') ) +
                        ( '' if skip is None else ' SKIP ' + str(skip) + ' ' ) +
                        ( '' if limit is None else ' LIMIT ' + str(limit) + ' ' ))

        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            nodes.append(node)
        return nodes

    def create_relation(self, relation, attributes, from_uuid, to_uuid, flatten=True, flattenList=True, agent_uuid=None):
        if flatten:
            attributes = json_utils.flatten_json(attributes, flattenList=flattenList)
        with self.neo4j_db.session() as session:
            rel = session.write_transaction(self._create_relation, relation, attributes, from_uuid, to_uuid, agent_uuid)

        if rel is None:
            return None
        return self._rel_toJSON(rel)

    def _create_relation(self, tx, relation, d, from_uuid, to_uuid, agent_uuid=None):
        result = tx.run(' MATCH (from {uuid: "' + from_uuid + '"})' + ', ' +  '(to {uuid: "' + to_uuid + '"}) ' +
                        ' CREATE (from) - [r: ' + relation + '] -> (to) ' +
                        ' '.join([ 'SET r.' + str(key) + ' = ' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' ' +
                        ' SET r._created_on = datetime() ' +
                        ' SET r._modified_on = datetime() ' +
                        ('' if agent_uuid  is None else (' SET r._created_by = "' + agent_uuid + '"' + ' SET r._modified_by = "' + agent_uuid + '" ')) +
                        ' RETURN r ')
        records = result
        rels = []
        for record in records:
            rel = record.items()[0][1]
            return rel
        return None


    def delete_relation(self, relation, from_uuid, to_uuid):
        with self.neo4j_db.session() as session:
            session.write_transaction(self._delete_relation, relation, from_uuid, to_uuid)

    def _delete_relation(self, tx, relation, from_uuid, to_uuid):
        result = tx.run(' MATCH (from {uuid: "' + from_uuid + '"})' + ', ' +  '(to {uuid: "' + to_uuid + '"}) ' + ', ' + ' (from) - [r: ' + relation + '] -> (to) ' +
                        ' DELETE r ')
        return




    def has_relation_between(self, from_uuid, to_uuid, relation=None):
        relations = self.get_relations_between(from_uuid, to_uuid, relation=relation)
        return len(relations) > 0

    def get_relations_between(self, from_uuid, to_uuid, relation=None):
        with self.neo4j_db.session() as session:
            rels = session.read_transaction(self._get_relations_between, from_uuid, to_uuid, relation)


        results = []
        for rel in rels:
            results.append(self._rel_toJSON(rel))
        return results

    def _get_relations_between(self, tx, from_uuid, to_uuid, relation):
        result = tx.run(' MATCH (from {uuid: "' + from_uuid + '"})' + ', ' +  '(to {uuid: "' + to_uuid + '"}) ' + ', ' +
                        ' (from) - ' +
                        (' [r] ' if relation is None else (' [r: ' + relation + '] ') ) +
                        '-> (to) ' +
                        ' RETURN r')

        records = result
        rels = []
        for record in records:
            rel = record.items()[0][1]
            rels.append(rel)
        return rels

    def set_relation_attributes(self, relation, attributes, from_uuid, to_uuid, flatten=True, flattenList=True, agent_uuid=None):
        if flatten:
            attributes = json_utils.flatten_json(attributes, flattenList=flattenList)
        with self.neo4j_db.session() as session:
            rel = session.write_transaction(self._set_relation_attributes, relation, attributes, from_uuid, to_uuid, agent_uuid)

        if rel is None:
            return None
        return self._rel_toJSON(rel)

    def _set_relation_attributes(self, tx, relation, d, from_uuid, to_uuid, agent_uuid=None):
        result = tx.run(' MATCH (from {uuid: "' + from_uuid + '"})' + ', ' +  '(to {uuid: "' + to_uuid + '"}) ' + ', ' + ' (from) - [r: ' + relation + '] -> (to) ' +
                        ' '.join([ 'SET r.' + str(key) + ' = ' + ( _safe_neo4j_attribute_value(d[key]) ) for key in list(d.keys())]) + ' ' +
                        ' SET r._modified_on = datetime() ' +
                        ('' if agent_uuid  is None else (' SET r._modified_by = "' + agent_uuid + '" ')) +
                        ' RETURN r')
        records = result
        rels = []
        for record in records:
            rel = record.items()[0][1]
            return rel
        return None

    def get_nodes_by_relation(self, uuid, relation=None, type=None, single=False, skip=None, limit=None):
        with self.neo4j_db.session() as session:
            nodes = session.read_transaction(self._get_nodes_by_relation, uuid, relation, type, skip, limit)

        if single:
            if len(nodes) > 0:
                node = nodes[0]
                return self._node_toJSON(node)
            else:
                return None
        else:
            results = []
            for node in nodes:
                results.append(self._node_toJSON(node))
            return results

    def _get_nodes_by_relation(self, tx, uuid, relation, t, skip, limit):
        result = tx.run(' MATCH (n {uuid: "' + uuid + '"}), ' +
                        (' (x), ' if t is None else ' (x: ' + t + '), ' ) +
                        ' (n) - ' +
                        (' [r] ' if relation is None else (' [r: ' + relation + '] ') ) +
                        ' - (x) ' +
                        ' RETURN x ' +
                        ( '' if skip is None else ' SKIP ' + str(skip) + ' ' ) +
                        ( '' if limit is None else ' LIMIT ' + str(limit) + ' ' ))

        records = result
        nodes = []
        for record in records:
            node = record.items()[0][1]
            nodes.append(node)
        return nodes


    def count_nodes_by_relation(self, uuid, relation=None, type=None):
        with self.neo4j_db.session() as session:
            result = session.read_transaction(self._count_nodes_by_relation, uuid, relation, type)

        return result

    def _count_nodes_by_relation(self, tx, uuid, relation, t):
        result = tx.run(' MATCH (n {uuid: "' + uuid + '"}), ' +
                        (' (x), ' if t is None else ' (x: ' + t + '), ' ) +
                        ' (n) - ' +
                        (' [r] ' if relation is None else (' [r: ' + relation + '] ') ) +
                        ' - (x) ' +
                        ' RETURN COUNT(x) ' )

        records = result
        for record in records:
            items = record.items()

            result = {}
            for item in items:
                key = item[0]
                value = item[1]

                return value

        return 0




    def count_nodes_by_type(self, type):
        with self.neo4j_db.session() as session:
            result = session.read_transaction(self._count_nodes_by_type, type)

        return result

    def _count_nodes_by_type(self, tx, t):
        result = tx.run(' MATCH (n: ' + t + ' ) ' +
                        ' RETURN COUNT(n) ' )

        records = result
        for record in records:
            items = record.items()

            result = {}
            for item in items:
                key = item[0]
                value = item[1]

                return value

        return 0

    def run_query(self, query, json_path_query=None, single=False, read=True, single_transaction=True):
        if not single_transaction:
            with self.neo4j_db.session() as session:
                results = self._run_session_query(session, query)
        else:
            with self.neo4j_db.session() as session:
                if read:
                    results = session.read_transaction(self._run_transaction_query, query)
                else:
                    results = session.write_transaction(self._run_transaction_query, query)

        return results if json_path_query is None else json_utils.json_query(results, json_path_query, single=single)

    def _run_session_query(self, session, query):
        resultset = session.run(query)
        records = resultset

        results = []
        for record in records:
            items = record.items()
            result = {}
            for item in items:
                key = item[0]
                value = item[1]

                result[key] = self._toJSON(value)
            results.append(result)

        return results

    def _run_transaction_query(self, tx, query):
        resultset = tx.run(query)
        records = resultset

        results = []
        for record in records:
            items = record.items()

            result = {}
            for item in items:
    
                key = item[0]
                value = item[1]

                result[key] = self._toJSON(value)
            results.append(result)

        return results

    def _toJSON(self, value):
        if type(value) in [bool, int, float, str]:
            return value
        elif type(value) == list:
            return [ self._toJSON(v) for v in value]
        elif type(value) == dict:
            return { key: self._toJSON(value[key]) for key in value.keys() }
        elif isinstance(value, neo4j.graph.Node):
            return self._node_toJSON(value)
        elif isinstance(value, neo4j.graph.Relationship):
            return self._rel_toJSON(value)
        else:
            return str(value)

    def _properties_toJSON(self, props):
        properties = copy.copy(props)
        for property in properties:
            value = properties[property]
            if type(value) in [bool, int, float, str, list]:
                continue
            else:
                properties[property] = str(value)
        return properties

    def _node_toJSON(self, node):
        node_json = self._properties_toJSON(node._properties)

        node_labels = list(node._labels)

        if len(node_labels) > 0:
            node_json['type'] = node_labels[0]

        return json_utils.unflatten_json(node_json, unflattenList=True)

    def _rel_toJSON(self, rel):
        rel_json = self._properties_toJSON(rel._properties)

        from_node = rel.start_node
        to_node = rel.end_node

        rel_json['from'] = self._node_toJSON(from_node)
        rel_json['to'] = self._node_toJSON(to_node)

        rel_json['type'] = rel.type


        return json_utils.unflatten_json(rel_json, unflattenList=True)
