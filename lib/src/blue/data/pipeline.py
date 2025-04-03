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
from blue.pubsub import Producer
from blue.stream import Message, MessageType, ContentType, ControlCode
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils

###############
### DataPipeline
#
class DataPipeline:
    def __init__(self, name="PIPELINE", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):

        self.name = name
        if id:
            self.id = id
        else:
            self.id = uuid_utils.create_uuid()

        if sid:
            self.sid = sid
        else:
            self.sid = self.name + ":" + self.id

        self.prefix = prefix
        self.suffix = suffix
        self.cid = cid

        if self.cid == None:
            self.cid = self.sid

            if self.prefix:
                self.cid = self.prefix + ":" + self.cid
            if self.suffix:
                self.cid = self.cid + ":" + self.suffix

        # pipeline stream
        self.producer = None

        self.agents = {}

        self._initialize(properties=properties)

        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def get_stream(self):
        return self.producer.get_stream()



    ###### DATA/METADATA RELATED
    def __get_json_value(self, value):
        if value is None:
            return None
        if type(value) is list:
            if len(value) == 0:
                return None
            else:
                return value[0]
        else:
            return value

    ## pipeline metadata
    def _init_metadata_namespace(self):
        # create namespaces for any pipeline common data
        self.connection.json().set(
            self._get_metadata_namespace(),
            "$",
            {"members": {}},
            nx=True,
        )

        # add created_date
        self.set_metadata("created_date", int(time.time()), nx=True)

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    def to_dict(self):
        metadata = self.get_metadata()
        return {
            "id": self.sid,
            "name": pydash.objects.get(metadata, "name", self.sid),
            "description": pydash.objects.get(metadata, "description", ""),
            "created_date": pydash.objects.get(metadata, "created_date", None),
            "created_by": pydash.objects.get(metadata, "created_by", None)
        }
    
    # TODO:
    def execute(self, plan, budget):
        return None

    ###### OPERATIONS
    def _start(self):
        # logging.info('Starting pipeline {name}'.format(name=self.name))
        self._start_connection()

        # initialize pipeline metadata
        self._init_metadata_namespace()

        # start  producer to emit pipeline events
        self._start_producer()

        logging.info("Started pipeline {cid}".format(cid=self.cid))

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()
        
    def _start_producer(self):
        # start, if not started
        if self.producer == None:

            producer = Producer(sid="PIPELINE", prefix=self.cid, properties=self.properties)
            producer.start()
            self.producer = producer

    def stop(self):
        # put EOS to stream
        self.producer.write_eos()

    def wait(self):
        while True:
            time.sleep(1)
