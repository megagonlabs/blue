###### Parsers, Formats, Utils
import argparse
import logging
import json

###############
### DataSource
#
class DataSource():
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # source protocol 
        self.properties['protocol'] = "default"

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

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
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()
        
        logging.info('Started source {name}'.format(name=self.name))

    def _stop(self):
        self._stop_connection()

        logging.info('Stopped source {name}'.format(name=self.name))

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### database
    def fetch_databases(self):
        return []

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

   ######### database/collection
    def fetch_database_collections(self, database):
        return []

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        return {}

    def execute_query(self, query, database=None, collection=None):
        return [{}]

