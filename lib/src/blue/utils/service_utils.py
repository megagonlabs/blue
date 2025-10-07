###### Parsers, Formats, Utils
import json
import re
import copy
import logging

###### Communication
from websockets.sync.client import connect


###### Blue
from blue.agent import Agent
from blue.utils import string_utils, json_utils


##########################
### ServiceClient
#
class ServiceClient:
    def __init__(self, name, properties=None):
        """Initialize ServiceClient to support calling external services.

        Parameters:
            name: Name of the service client.
            properties: Properties for the service client.
        """
        self.name = name

        self._initialize(properties=properties)

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # service url
        self.properties['service_url'] = "ws://localhost:8001"

        # input / output processing properties
        self.properties['input_json'] = None
        self.properties['input_context'] = None
        self.properties['input_context_field'] = None
        self.properties['input_field'] = 'input'
        self.properties['output_path'] = 'output'

        # overrride with additional properties if needed
        # properties to pass on to API call should have a prefix of self.name

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def get_properties(self, properties=None):
        """Get properties, overriding with provided properties.

        Parameters:
            properties: Properties to override.

        Returns:
            Merged properties.
        """
        if properties is None:
            properties = {}
        return json_utils.merge_json(self.properties, properties)

    def extract_input_params(self, input_data, properties=None):
        """Extract input parameters from input data based on optional properties.

        Parameters:
            input_data: Input data to extract parameters from.
            properties: Optional properties to use for extraction

        Returns:
            Extracted input parameters.
        """
        properties = self.get_properties(properties=properties)

        return {"input": input_data}

    def extract_output_params(self, output_data, properties=None):
        """Extract output parameters from output data based on optional properties.

        Parameters:
            output_data: Output data to extract parameters from.
            properties: Optional properties to use for extraction

        Returns:
            Extracted output parameters.
        """
        properties = self.get_properties(properties=properties)
        return {}

    def extract_api_properties(self, properties=None):
        """Extract API-related properties based on service prefix.

        Parameters:
            properties: Optional properties to override.

        Returns:
            Extracted API properties.
        """
        properties = self.get_properties(properties=properties)

        api_properties = {}

        # api properties have a prefix of name, e.g. openai.model
        for p in properties:
            if p.find(self.get_service_prefix()) == 0:
                property = p[len(self.get_service_prefix()) + 1 :]
                api_properties[property] = properties[p]

        return api_properties

    def create_message(self, input_data, properties=None, additional_data=None):
        """Create message to send to service based on input data and properties.

        Parameters:
            input_data: Input data to create the message.
            properties: Optional properties to override.
            additional_data: Additional data to be used for creating the message.

        Returns:
            Created message.
        """
        # add properties to pass onto api
        message = self.extract_api_properties(properties=properties)

        properties = self.get_properties(properties=properties)

        if additional_data is None:
            additional_data = {}
        ## prepare input
        if 'input_template' in properties and properties['input_template'] is not None:
            input_template = properties['input_template']
            input_params = self.extract_input_params(input_data, properties=properties)
            input_data = string_utils.safe_substitute(input_template, **properties, **input_params, **additional_data)

        # set input text to message
        input_object = input_data

        if 'input_json' in properties and properties['input_json'] is not None:
            input_object = {}
            if type(properties['input_json']) == str:
                input_object = json.loads(properties['input_json'])
            else:
                input_object = copy.deepcopy(properties['input_json'])

            # set input text in object
            json_utils.json_query_set(input_object, properties['input_context_field'], input_data, context=properties['input_context'])

        message[properties['input_field']] = input_object
        return message

    def create_output(self, response, properties=None):
        """Create output from service response based on properties.

        Parameters:
            response: Service response to create output from.
            properties: Optional properties to override.
        Returns:
            Created output.
        """
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        output_data = json_utils.json_query(response, properties['output_path'], single=True)

        # pre-process output from response
        output_data = self._preprocess_output(output_data, properties=properties)

        # apply output template
        if 'output_template' in properties and properties['output_template'] is not None:
            output_template = properties['output_template']
            output_params = self.extract_output_params(output_data, properties=properties)
            output_data = string_utils.safe_substitute(output_template, **properties, **output_params, output=output_data)
        return output_data

    def validate_input(self, input_data, properties=None):
        """Validate input data based on properties.

        Parameters:
            input_data: Input data to validate.
            properties: Optional properties to override.

        Returns:
            True if input is valid, False otherwise.
        """
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        return True

    def process_output(self, output_data, properties=None):
        """Process output data based on properties, such as casting.
        Parameters:
            output_data: Output data to process.
            properties: Optional properties to override.

        Returns:
            Processed output data.
        """
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
            elif properties['output_cast'].lower() == "str":
                output_data = str(output_data)

        return output_data

    def _preprocess_output(self, output_data, properties=None):
        """Preprocess output data based on properties, such as stripping and transformations.

        Parameters:
            output_data: Output data to preprocess.
            properties: Optional properties to override.

        Returns:
            Preprocessed output data.
        """
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # string transformations
        if type(output_data) == str:

            # strip
            if 'output_strip' in properties:
                output_data = output_data.strip()

            # re transformations
            if 'output_transformations' in properties:
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

    def execute_api_call(self, input, properties=None, additional_data=None):
        """Execute API call to the service with the given input and properties.

        Parameters:
            input: Input data for the API call.
            properties: Optional properties to override.
            additional_data: Additional data to be used for creating the message for the API call.

        Returns:
            Output from the service after processing.
        """
        # create message from input
        message = self.create_message(input, properties=properties, additional_data=additional_data)

        # serialize message, call service
        url = self.get_service_address(properties=properties)
        m = json.dumps(message)
        r = self.call_service(url, m)

        response = json.loads(r)

        # create output from response
        output = self.create_output(response, properties=properties)

        # process output data
        output = self.process_output(output, properties=properties)

        return output

    def get_service_prefix(self):
        """Get service prefix from properties.

        Returns:
            Service prefix.
        """
        service_prefix = self.name.lower()
        if 'service_prefix' in self.properties:
            service_prefix = self.properties['service_prefix']
        return service_prefix

    def get_service_address(self, properties=None):
        """Get service address (URL) from properties.

        Parameters:
            properties: Optional properties to override.

        Returns:
            Service address (URL).
        """
        properties = self.get_properties(properties=properties)
        if 'service_url' in properties:
            return properties['service_url']
        return None

    def call_service(self, url, data):
        """Call the service at the given URL with the provided data.

        Parameters:
            url: Service URL.
            data: Data to send to the service.

        Returns:
            Response from the service.
        """
        logging.info("sending data to:" + str(url))
        logging.info(str(data))
        with connect(url) as websocket:
            websocket.send(data)
            message = websocket.recv()
            return message
