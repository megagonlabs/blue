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
### Operator
#
class Operator():
    def __init__(
        self,
        name="OPERATOR",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        pipeline=None,
        processor=None,
        properties={},
    ):

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

        self._initialize(properties=properties)

        # override, if necessary
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs, properties=self.properties)
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(*args, **kwargs, properties=self.properties)

        # pipeline
        self.pipeline = pipeline

        # consumer for instruction pipeline stream
        self.pipeline_consumer = None

        # workers of operator 
        self.workers = []

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # instructable
        self.properties["instructable"] = True
        

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ###### worker
    # input_stream is data stream for operator
    def create_worker(self, input_stream, context=None, processor=None):
        # listen 
        logging.info(
            "Creating worker for stream {stream} ...".format(stream=input_stream)
        )

        if processor == None:
            processor = lambda *args, **kwargs: self.processor(*args, **kwargs)

        # set prefix if context provided
        if context:
            p = context + ":" + self.sid
        else:
            # default operator's cid is prefix
            p = self.cid

        worker = Worker(
            input_stream,
            prefix=p,
            processor=processor,
            properties=self.properties,
        )

        self.workers.append(worker)

        return worker

    ###### default processor, override
    def default_processor(
        self,
        data, #JSON
        properties=None,
    ):
        logging.info("default_processor: override")
        logging.info(data)
        logging.info(properties)

    ###### instruction pipeline listener, do not override
    def pipeline_listener(self, message):
        if message.getCode() == ControlCode.EXECUTE_OPERATOR:
            operator = message.getArg("operator")
            if operator == self.name:
                context = message.getArg("context")
                input_stream = message.getArg("input")
                self.create_worker(input_stream, context=context)


    def _start(self):
        self._start_connection()

        # if operator is associated with a pipeline
        if self.pipeline:
            self._start_pipeline_consumer()

        logging.info("Started operator {name}".format(name=self.name))

    def _start_pipeline_consumer(self):
        # start a consumer to listen to instruction pipeline
        if self.pipeline:
            self.pipeline_consumer = Consumer(
                self.pipeline,
                name=self.name,
                listener=lambda message: self.pipeline_listener(message),
                properties=self.properties,
            )
            self.pipeline_consumer.start()

    def stop(self):

        # send stop to each worker
        for w in self.workers:
            w.stop()

    def wait(self):
        # send wait to each worker
        for w in self.workers:
            w.wait()
        
    

###################
### OperatorFactory
#
class OperatorFactory():
    def __init__(
        self,
        _class=Operator,
        _name="Operator",
        _registry="default",
        platform="default",
        properties={},
    ):
        self._class = _class
        self._name = _name
        self._registry = _registry

        self.platform = platform

        self._initialize(properties=properties)

        self.platform = None

        # creation time
        self.ct = math.floor(time.time_ns() / 1000000)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()
        
    ###### factory functions
    def create(self, **kwargs):
        print(kwargs)
        klasse = self._class
        instanz = klasse(**kwargs)
        return instanz

    def _start(self):
        self._start_connection()

        self._start_consumer()
        logging.info(
            "Started operator factory for operator: {name} in registry: {registry} on platform: {platform} ".format(
                name=self._name,
                registry=self._registry,
                platform=self.platform,
            )
        )

    def wait(self):
        self.platform_consumer.wait()

    def _start_consumer(self):
        # platform stream
        stream = "PLATFORM:" + self.platform + ":STREAM"
        self.platform_consumer = Consumer(
            stream,
            name=self._name + "_FACTORY",
            listener=lambda message: self.platform_listener(message),
            properties=self.properties,
        )
        self.platform_consumer.start()

    def platform_listener(self, message):
        # listen to platform stream

        logging.info("Processing: " + str(message))
        id = message.getID()

        # only process newer instructions
        mt = int(id.split("-")[0])

        # ignore past instructions
        if mt < self.ct:
            return

        # check if join pipeline
        if message.getCode() == ControlCode.JOIN_PIPELINE:
            pipeline = message.getArg("pipeline")
            registry = message.getArg("registry")
            operator = message.getArg("operator")
            

            # start with factory properties
            properties_from_pipeline = message.getArg("properties")
            properties_from_factory = self.properties
            operator_properties = {}
            operator_properties = json_utils.merge_json(operator_properties, properties_from_factory)
            operator_properties = json_utils.merge_json(operator_properties, properties_from_pipeline)

            if self._name == operator:
                name = operator

                logging.info("Launching Operator: " + name + "...")
                logging.info("Operator Properties: " + json.dumps(operator_properties) + "...")

                prefix = pipeline + ":" + "OPERATOR"
                a = self.create(
                    name=name,
                    prefix=prefix,
                    pipeline=pipeline,
                    properties=operator_properties,
                )

                logging.info("Joined pipeline: " + pipeline)


###############
### Worker
#
class Worker:
    def __init__(
        self,
        input_stream,
        name="WORKER",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        processor=None,
        properties={},
    ):

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

        self.input = input

        self._initialize(properties=properties)

        self.input_stream = input_stream
        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

        self.properties = properties

        self.producer = None
        self.consumer = None

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}
        self.properties["num_threads"] = 1
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def listener(self, message, input="DEFAULT"):
        
        r = None
        if self.processor is not None:
            # only data messages
            if message.isData(): 
                d = message.getData()           
                r = self.processor(d)

        if r is None:
            return
        
        results = []
        if type(r) == list:
            results = r
        else:
            results = [r]


        for result in results:
            if type(result) in [int, float, str, dict]:
                self.write_data(result)
            else:
                # error
                logging.error("Unknown return type from processor function: " + str(result))
                return

    def write_bos(self):
        self.write(Message.BOS)

    def write_eos(self):
        self.write(Message.EOS)

    def write_data(self, data):
        if type(data) == int:
            contents = data
            content_type = ContentType.INT
        elif type(data) == float:
            contents = data
            content_type = ContentType.FLOAT
        elif type(data) == str:
            contents = data
            content_type = ContentType.STR
        elif type(data) == dict:
            contents = data
            content_type = ContentType.JSON

        self.write(Message(MessageType.DATA, contents, content_type))

    def write(self, message, output="DEFAULT", tags=None):
        # create producer, if not existing
        producer = self._start_producer()
        producer.write(message)

        # close consumer, if end of stream
        if message.isEOS():
            # done, stop listening to input stream
            if self.consumer:
                self.consumer.stop()

    def _start(self):
        # start consumer only first on initial given input_stream
        self._start_consumer()
        logging.info("Started operator worker {name}".format(name=self.sid))

    def _start_consumer(self):
        # start a consumer to listen to stream
        if self.input_stream is None:
            return
        
        consumer = Consumer(
            self.input_stream,
            name=self.name,
            prefix=self.cid,
            listener=lambda message: self.listener(message, input=self.input),
            properties=self.properties,
        )

        self.consumer = consumer
        consumer.start()

    def _start_producer(self):
        # create producer for output
        producer = Producer(name="OUT", prefix=self.prefix, suffix="STREAM", properties=self.properties)
        producer.start()
        self.producer = producer

        return producer


    def stop(self):
        # send stop signal to consumer(s)
        if self.consumer:
            self.consumer.stop()

    def wait(self):
        # send wait to consumer(s)
        if self.consumer:
            self.consumer.wait()

###############
### OperatorRegistry
#
class OperatorRegistry(Registry):
    def __init__(self, name="OPERATOR_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

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
        return super().get_record(operator, 'operator')

    def get_operator_description(self, operator):
        return super().get_record_description(operator, '/')

    def set_operator_description(self, operator, description, rebuild=False):
        super().set_record_description(operator, '/', description, rebuild=rebuild)

    # operator properties
    def get_operator_properties(self, operator):
        return super().get_record_properties(operator, '/')

    def get_operator_property(self, operator, key):
        return super().get_record_property(operator, '/', key)

    def set_operator_property(self, operator, key, value, rebuild=False):
        super().set_record_property(operator, '/', key, value, rebuild=rebuild)

    def delete_operator_property(self, operator, key, rebuild=False):
        super().delete_record_property(operator, '/', key, rebuild=rebuild)

    # operator image (part of properties)
    def get_operator_image(self, operator):
        return self.get_operator_property(operator, 'image')

    def set_operator_image(self, operator, image, rebuild=False):
        self.set_operator_property(operator, 'image', image, rebuild=rebuild)