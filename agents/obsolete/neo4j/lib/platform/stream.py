import sys

###### Backend, Databases
import redis
from redis.commands.json.path import Path
import pydash


###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/utils/")

###### Blue
from producer import Producer
from session import Session
from message import Message, MessageType, ContentType, ControlCode
from connection import PooledConnectionFactory

class Stream:
    def __init__(self, cid, properties={}):
        self.cid = cid
        self._initialize(properties=properties)
        self._start_connection()

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

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

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
