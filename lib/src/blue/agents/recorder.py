###### Parsers, Formats, Utils
import logging


###### Blue
from blue.agent import Agent
from blue.stream import ContentType
from blue.utils import json_utils


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


############################
### Agent.RecorderAgent
#
class RecorderAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "RECORDER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()


        # default properties
        listeners = {}
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners

        self.properties['listens'] = listeners
        default_listeners['includes'] = ['JSON']
        default_listeners['excludes'] = [self.name]

        # recorder is an aggregator agent
        self.properties['aggregator'] = True 
        self.properties['aggregator.eos'] = 'NEVER'

        # recorder config
        records = []
        self.properties['records'] = records
        records.append({"variable":"all","query":"$","single":True})


    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if message.isEOS():
            return None
        elif message.isBOS():
            pass
        elif message.isData():
            # store data value
            data = message.getData()

            # TODO: Record from other data types
            if message.getContentType() == ContentType.JSON:
                if 'records' in self.properties:
                    records = self.properties['records']
                    variables = []
                    for record in records:
                        variable = record['variable']
                        query = record['query']
                        single = False
                        if 'single' in record:
                            single = record['single']

                        # evaluate path on json_data
                        logging.info('Executing query {query}'.format(query=query))
                        result = None
                        try:
                            result = json_utils.json_query(data, query, single=single)
                        except:
                            pass 

                        if result:
                            worker.set_session_data(variable, result)
                            variables.append(variable)
                    
                    if len(variables) > 0:
                        return variables

    
        return None
