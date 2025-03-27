###### Parsers, Formats, Utils
import logging
import uuid

###### Blue
from blue.connection import PooledConnectionFactory

###############
### DataPlanner
#
class DataPlanner():
    def __init__(self, name="DATA_PLANNER", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        
        self.name = name
        if id:
            self.id = id
        else:
            self.id = str(hex(uuid.uuid4().fields[0]))[2:]

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

        self._initialize(properties=properties)

        self._start()   
        
    ###### initialization
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

    def plan(self, input_data, task, context):
        return None
    
    def optimize(self, plan, budget):
        return None

    ######
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()
        
    def _start(self):
        self._start_connection()

        logging.info('Started data planner {name}'.format(name=self.name))
