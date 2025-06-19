"""
The NL2LLMAgent aims to utilize LLM models' internal knowledge to answer natural language queries.
It works with any data source that has "llm" as their protocol.
"""

###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.data.registry import DataRegistry

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

##########################
### Agent.NL2LLMAgent

class NL2LLMAgent(Agent):

    PROPERTIES = {
        # agent related properties
        "nl2llm_source": None, 
        "nl2llm_discovery": True, # if True, will search for any source that has "llm" as their protocol in the data registry, if false, will just use the "openai" source
        "nl2llm_discovery_source_protocols": ["openai"], # list of protocols to search for, should be changed to ["llm"] after github issue #945 is resolved
        "nl2llm_context": [],
        "nl2llm_attr_names": [],

        # output related properties
        "nl2llm_output_filters": ["all"],
        "nl2llm_output_max_results": None, # if not None, it will limit the number of records in returned json array 
        
        # agent configuration
        "listens": {
            "DEFAULT": {
                "includes": ["USER"],
                "excludes": []
            }
        }
    }
    
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2LLM"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # initialize default properties
        for key in NL2LLMAgent.PROPERTIES:
            self.properties[key] = NL2LLMAgent.PROPERTIES[key]

    def _start(self):
        super()._start()

        # initialize registry
        self._init_registry()

        # initialize source
        self._init_source()

    def _init_registry(self):
        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix, properties=self.properties)

    def _init_source(self):
        """Initialize the source for the agent.
        """
        # initialize optional settings
        self.selected_source = None
        self.selected_source_protocol = None

        # select source, if set
        if "nl2llm_source" in self.properties and self.properties["nl2llm_source"]:
            self.selected_source = self.properties["nl2llm_source"]

            source_properties = self.registry.get_source_properties(self.selected_source)

            if source_properties:
                if 'connection' in source_properties:
                    connection_properties = source_properties["connection"]

                    protocol = connection_properties["protocol"]
                    if protocol:
                        self.selected_source_protocol = protocol
                    if 'protocol_variant' in source_properties:
                        self.selected_source_protocol_variant = source_properties.get("protocol_variant", None)
                    logging.info(f"selected source: {self.selected_source}")
                    logging.info(f"selected source protocol: {self.selected_source_protocol}")
                    logging.info(f"selected source protocol variant: {self.selected_source_protocol_variant}")
        else:
            ## discover llm sources
            scope = None
            sources = self._search_sources(scope=scope)
            # return only the first available source
            if sources:
                self.selected_source = sources[0]
                self.selected_source_protocol = self.registry.get_source_properties(self.selected_source)['connection']['protocol']
                self.selected_source_protocol_variant = self.registry.get_source_properties(self.selected_source)['connection']['protocol_variant']
    
    # def _parse_data_scope(self, scope):
    #     """Parse the scope of a data source.
    #     """
    #     source = None

    #     if scope:
    #         sa = scope.split("/")
    #         if len(sa) > 2:
    #             source = sa[2]
    #             if source == '':
    #                 source = None

    #     return source
    
    
    def _search_sources(self, scope=None):
        """Search the data registry for sources that match the question.
        """
        sources = []
        
        if scope:
            # search within specific scope
            sources = self.registry.list_records(type='source', scope=scope, recursive=False)
        else:
            # search all sources
            sources = self.registry.list_records(type='source', scope='/', recursive=False)
        
        # filter sources by protocol if discovery protocols are specified
        if 'nl2llm_discovery_source_protocols' in self.properties:
            protocols = self.properties['nl2llm_discovery_source_protocols']
            filtered_sources = []
            
            for source_record in sources:
                source_name = source_record.get('name')
                if source_name:
                    source_properties = self.registry.get_source_properties(source_name)
                    if source_properties and 'connection' in source_properties:
                        connection_properties = source_properties['connection']
                        protocol = connection_properties.get('protocol')
                        if protocol in protocols:
                            filtered_sources.append(source_name)
            
            sources = filtered_sources
        
        return sources

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process incoming messages and execute LLM queries."""
        
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # get input data
        input_data = message.getData()
        
        # process the query
        result = self.process_query(input_data, properties=properties)
        
        # write result to output stream
        if worker:
            worker.write_data(result)
        
        return result

    def process_query(self, question, properties=None):
        """Process a natural language query using the selected LLM source.
        """
        
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        try:
            # connect to the source
            source_connection = self.registry.connect_source(self.selected_source)
            
            # execute query
            logging.info(f"source: {self.selected_source}")
            logging.info(f"executing query: {question}")
            
            result = source_connection.execute_query(
                question,
                context=properties.get('nl2llm_context', ""),
                attr_names=properties.get('nl2llm_attr_names', [])
            )
            
            logging.info("result: " + str(result))
            
            # apply output filters
            filtered_result = self._apply_filter({
                'question': question,
                'source': self.selected_source,
                'result': result,
                'error': None
            }, properties=properties)
            
            return filtered_result

        except Exception as e:
            error = str(e)
            logging.error(f"Error executing query: {error}")
            
            # apply output filters
            filtered_result = self._apply_filter({
                'question': question,
                'source': self.selected_source,
                'result': None,
                'error': error
            }, properties=properties)
            
            return filtered_result

    def _apply_filter(self, output):
        """Apply output filters to the result.
        """
        output_filters = ['all']

        if 'nl2llm_output_filters' in self.properties:
            output_filters = self.properties['nl2llm_output_filters']

        question = output['question']
        source = output['source']
        result = output['result']
        error = output['error']

        # max results
        if "nl2llm_output_max_results" in self.properties and self.properties['nl2llm_output_max_results']:
            output_max_results = int(self.properties['nl2llm_output_max_results'])
            if isinstance(result, list):
                result = result[:output_max_results]

        message = None
        if 'all' in output_filters:
            message = {
                'question': question,
                'source': source,
                'result': result,
                'error': error
            }
            return message
            
        elif len(output_filters) == 1:
            if 'question' in output_filters:
                message = question
            if 'source' in output_filters:
                message = source
            if 'error' in output_filters:
                message = error
            if 'result' in output_filters:
                message = result
        else:
            message = {}
            if 'question' in output_filters:
                message['question'] = question
            if 'source' in output_filters:
                message['source'] = source
            if 'result' in output_filters:
                message['result'] = result
            if 'error' in output_filters:
                message['error'] = error
        
        return message 