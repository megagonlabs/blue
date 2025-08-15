###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.utils import log_utils


###############
### DataSource
#
class DataSource:
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        self.properties = {}

        # connection properties
        self._initialize_connection_properties()

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_connection_properties(self):
        connection_properties = {}

        connection_properties['protocol'] = 'default'
        self.properties['connection'] = connection_properties

    def _initialize_logger(self):
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("source", self.name, -1)

    ###### connection
    def _start_connection(self):
        connection = self.properties['connection']

        self.connection = self._connect(**connection)

    def _stop_connection(self):
        self._disconnect()

    def _connect(self, **connection):
        return None

    def _disconnect(self):
        return None

    def _start(self):
        # self.logger.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        self.logger.info('Started source {name}'.format(name=self.name))

    def _stop(self):
        self._stop_connection()

        self.logger.info('Stopped source {name}'.format(name=self.name))

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### source/database
    def fetch_databases(self):
        return []

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

    def create_database(self, database, properties={}):
        return {}

    ######### source/database/collection
    def fetch_database_collections(self, database):
        return []

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        return {}

    def create_database_collection(self, database, collection, properties={}):
        return {}

    ######### source/database/collection/entity
    # properties: {
    #     "properties": [    <--- entity properties
    #         {
    #             "name": "",
    #             "type": "",
    #             "misc":
    #         }
    #      ]
    # }
    # note: misc can include primary key, etc. features that are db specific
    #
    def create_database_collection_entity(self, database, collection, entity, properties={}):
        return {}

    ######### source/database/collection/relation
    def create_database_collection_relation(self, database, collection, relation, properties={}):
        return {}

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        return [{}]

    #######  stats ############
    def fetch_source_stats(self):
        return None

    def fetch_database_stats(self, database):
        return None

    def fetch_collection_stats(self, database, collection_name, schema_json=None, sample_limit=None):
        return None

    def fetch_entity_stats(self, database, collection, entity):
        return None

    def fetch_property_stats(self, database, collection, entity, property_name, sample_limit=None):
        return None
