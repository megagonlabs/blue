###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.stream import ContentType
from blue.data.registry import DataRegistry


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(ascstime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


############################
### Agent.QueryExecutorAgent
#
class QueryExecutorAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "QUERYEXECUTOR"
        super().__init__(**kwargs)

    def _start(self):
        super()._start()

        # initialize registry
        self._init_registry()

    def _init_registry(self):
        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix, properties=self.properties)
                       

    def execute_sql_query(self, path, query):
        result = None
        question = None
        error = None
        try:
            # extract source, database, collection
            _, source, database, collection = path.split('/')
            # connect
            source_connection  = self.registry.connect_source(source)
            # execute query
            result = source_connection.execute_query(query, database=database, collection=collection)
        except Exception as e:
            error = str(e)

        return {
            'question': question,
            'source': path,
            'query': query,
            'result': result,
            'error': error
        }
    
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        ##### Upon USER/Agent input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                # extract json
                input = " ".join(worker.get_data(stream))

                # logging.info("input: "  + input)
                
                if worker:
                    try:
                        data = json.loads(input)
                    except:
                        logging.error("Input is not JSON")
                        return

                    # extract path, query
                    path = data['source']
                    query = data['query']
                    result = self.execute_sql_query(path, query)
                    return [result, message.EOS]
                
            elif message.isBOS():
                stream = message.getStream()

                # init private stream data to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                stream = message.getStream()

                if message.getContentType() == ContentType.JSON:
                    # extract path, query
                    path = data['source']
                    query = data['query']
                    result = self.execute_sql_query(path, query)
                    return [result, message.EOS]
                else:
                    # append to private stream data
                    if worker:
                        worker.append_data(stream, data)