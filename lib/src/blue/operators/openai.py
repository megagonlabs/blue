###### Parsers, Formats, Utils
import logging

###### Blue
from blue.operators.requestor import RequestorOperator

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


class OpenAIOperator(RequestorOperator):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "OPENAI"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['openai.service'] = "ws://localhost:8003"

        self.properties['openai.api'] = 'Completion'
        self.properties['openai.model'] = "text-davinci-003"
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'prompt'
        self.properties['output_path'] = '$.choices[0].text'
        self.properties['openai.stream'] = False
        self.properties['openai.max_tokens'] = 50

        # prefix for service specific properties
        self.properties['service.prefix'] = 'openai'
