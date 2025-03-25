###### Parsers, Formats, Utils
import logging
import json
import re
import copy

###### Communication
from websockets.sync.client import connect


###### Blue
from blue.agent import Agent
from blue.utils import string_utils, json_utils



# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

############################
### Agent.RequestorAgent
#
class RequestorAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "REQUESTOR"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['api.service'] = "ws://localhost:8001"
    
        self.properties['input_json'] = None
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'input'
        self.properties['output_path'] = 'output'

    def get_prefix(self):
        prefix = self.name.lower()
        if 'service.prefix' in self.properties:
            prefix = self.properties['service.prefix']
        return prefix + '.'


    def get_properties(self, properties=None):
        merged_properties = {}

        # copy agent properties
        for p in self.properties:
            merged_properties[p] = self.properties[p]

        # override
        if properties is not None:
            for p in properties:
                merged_properties[p] = properties[p]

        return merged_properties
    
    def extract_input_params(self, input_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        return {}
    
    def extract_output_params(self, output_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)
        return {}
    
    def create_message(self, input_data, properties=None):
        message = {}

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # set all message attributes from properties,
        # and only those with api prefix 
        for p in properties:
            if p.find(self.get_prefix()) == 0:
                # do not pass forward service property
                property = p[len(self.get_prefix()):]
                if property == 'service':
                    continue
                message[property] = properties[p]

       
        if 'input_template' in properties and properties['input_template'] is not None:
            input_template = properties['input_template']
            input_params = self.extract_input_params(input_data, properties=properties)
            session_params = self.session.get_all_data()
            if session_params is None:
                session_params = {}
            input_data = string_utils.safe_substitute(input_template, **properties, **input_params, **session_params, input=input_data)

        # set input text to message
        input_object = input_data

        if 'input_json' in properties and properties['input_json'] is not None:
            input_object = {}
            if type(properties['input_json']) == str:
                input_object = json.loads(properties['input_json'])
            else:
                input_object = copy.deepcopy(properties['input_json'])
                
            # set input text in object
            json_utils.json_query_set(input_object,properties['input_context_field'], input_data, context=properties['input_context'])

        message[properties['input_field']] = input_object
        return message

    def create_output(self, response, properties=None):

        
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        output_data = json_utils.json_query(response, properties['output_path'], single=True)
        
        logging.info(output_data)
        logging.info(type(output_data))

        # pre-process output from response
        output_data = self._preprocess_output(output_data, properties=properties)

        # apply output template
        if 'output_template' in properties and properties['output_template'] is not None:
            output_template = properties['output_template']
            output_params = self.extract_output_params(output_data, properties=properties)
            output_data = string_utils.safe_substitute(output_template, **properties, **output_params, output=output_data)
        return output_data

    def validate_input(self, input_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        return True 

    def process_output(self, output_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # cast
        if 'output_cast' in properties:
            if properties['output_cast'].lower() == "int":
                output_data = int(output_data)
            elif properties['output_cast'].lower() == "float":
                output_data = float(output_data)
            elif properties['output_cast'].lower() == "json":
                output_data = json.loads(output_data)

        return output_data

    def _preprocess_output(self, output_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # string transformations
        if type(output_data) == str:

            # strip
            if 'output_strip' in properties:
                logging.info("output_strip")
                output_data = output_data.strip()

            # re transformations
            if 'output_transformations' in properties:
                logging.info("output_transformations")
                transformations = properties['output_transformations']
                for transformation in transformations:
                    tf = transformation['transformation']
                    if tf == 'replace':
                        tfrom = transformation['from']
                        tto = transformation['to']
                        output_data = output_data.replace(tfrom, tto)
                    elif tf == 'sub':
                        tfrom = transformation['from']
                        tto = transformation['to']
                        tfromre = re.compile(tfrom)
                        ttore = re.compile(tfrom)
                        output_data = re.sub(tfromre, ttore, output_data)

                
        return output_data

    def handle_api_call(self, stream_data, properties=None):
        # create message, copying API specific properties
        input_data = " ".join(stream_data)
        if not self.validate_input(input_data, properties=properties):
            return 

        logging.info(input_data)
        message = self.create_message(input_data, properties=properties)

        # serialize message, call service
        m = json.dumps(message)
        r = self.call_service(m)

        response = json.loads(r)

        # create output from response
        output_data = self.create_output(response, properties=properties)

        # process output data
        output_data = self.process_output(output_data, properties=properties)

        return output_data

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        
        if message.isEOS():
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')

            #### call api to compute
            worker.write_data(self.handle_api_call(stream_data, properties=properties))
            worker.write_eos()
            
        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            logging.info(data)
            
            if worker:
                worker.append_data('stream', str(data))
        
        return None

    def get_service_address(self):
        service_address = self.properties['api.service']
        if self.get_prefix() + "service" in self.properties:
            service_address = self.properties[self.get_prefix() + "service"]

        return service_address
        
    def call_service(self, data):
        with connect(self.get_service_address()) as websocket:
            logging.info("Sending to service: {data}".format(data=data))
            websocket.send(data)
            message = websocket.recv()
            logging.info("Received from service: {message}".format(message=message))
            return message
