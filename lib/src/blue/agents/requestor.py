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
from blue.utils.service_utils import ServiceClient


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S"
)


############################
### Agent.RequestorAgent
#
class RequestorAgent(Agent, ServiceClient):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "REQUESTOR"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['service_url'] = "ws://localhost:8001"

        # input / output processing properties
        self.properties['input_json'] = None
        self.properties['input_context'] = None
        self.properties['input_context_field'] = None
        self.properties['input_field'] = 'input'
        self.properties['output_path'] = 'output'

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        if message.isEOS():
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')

            #### call api to compute
            input_data = stream_data[0]
            self.logger.info(input_data)
            session_data = self.session.get_all_data()
            output = self.execute_api_call(input_data, properties=properties, additional_data=session_data)
            worker.write_data(output)
            worker.write_eos()

        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream', [])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            self.logger.info(data)

            if worker:
                worker.append_data('stream', str(data))

        return None
