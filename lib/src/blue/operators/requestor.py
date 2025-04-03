###### Parsers, Formats, Utils
import logging
import time
import json

###### Communication
from websockets.sync.client import connect


###### Blue
from blue.operator import Operator
from blue.utils import string_utils, json_utils

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


class RequestorOperator(Operator):
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

        # copy operator properties
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
            input_data = string_utils.safe_substitute(input_template, **properties, **input_params, input=input_data)

        # set input text to message
        input_object = input_data

        if 'input_json' in properties and properties['input_json'] is not None:
            input_object = json.loads(properties['input_json'])
            # set input text in object
            json_utils.json_query_set(input_object,properties['input_context_field'], input_data, context=properties['input_context'])

        message[properties['input_field']] = input_object
        return message

    def create_output(self, response, properties=None):

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        output_data = json_utils.json_query(response, properties['output_path'], single=True)
           
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
        output = self.process_output(output_data, properties=properties)

        return output

    def default_processor(self, data, properties=None):
        
        #### call api to compute
        return self.handle_api_call(data, properties=properties)


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
