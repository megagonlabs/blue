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


##########################
### Agent.NL2LLMAgent
#
class NL2LLMAgent(Agent):
    """An agent that processes natural language queries using LLM models.
    It can be configured to use a specific LLM source or discover available LLM sources in the data registry.
    The agent sends the query to the selected LLM source and returns the response as structured data.
    
    Properties (in addition to Agent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `nl2llm_source`  | `str`                 | `None`     | The name of the LLM source to use. If None, the agent will discover available LLM sources in the data registry. |
    | `nl2llm_discovery` | `bool`              | `True`     | If True, the agent will search for any source that has "llm" as their protocol in the data registry. |
    | `nl2llm_discovery_source_protocols` | `list of str` | `["openai"]` | List of protocols to search for. Should be changed to `["llm"]` after github issue #945 is resolved. |
    | `nl2llm_context` | `list of str`        | `[]`       | Optional context to provide to the LLM source for query processing. |
    | `nl2llm_attr_names` | `list of str`   | `[]`       | Optional attribute names to provide to the LLM source for query processing. |
    | `nl2llm_output_filters` | `list of str` | `["all"]` | Output filters to apply to the result. Options are "all", "question", "source", "result", "error". |
    | `nl2llm_output_max_results` | `int or None` | `None` | If not None, limits the number of records in the returned JSON array. |

    Inputs:
    - DEFAULT: natural language query
    
    Outputs:
    - DEFAULT: query results, tagged as `QUERY` and `NL`

    """

    PROPERTIES = {
        # agent related properties
        "nl2llm_source": None,
        "nl2llm_discovery": True,  # if True, will search for any source that has "llm" as their protocol in the data registry, if false, will just use the "openai" source
        "nl2llm_discovery_source_protocols": ["openai"],  # list of protocols to search for, should be changed to ["llm"] after github issue #945 is resolved
        "nl2llm_context": [],
        "nl2llm_attr_names": [],
        # output related properties
        "nl2llm_output_filters": ["all"],
        "nl2llm_output_max_results": None,  # if not None, it will limit the number of records in returned json array
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

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the NL2LLM agent."""
        self.add_input("DEFAULT", description="natural language query")

    def _initialize_outputs(self):
        """Initialize outputs for the NL2LLM agent, tags the output as QUERY and NL."""
        self.add_output("DEFAULT", description="query results", tags=["QUERY", "NL"])

    def _start(self):
        """Start the NL2LLM agent."""
        self.logger.info("NL2LLMAgent _start() called")
        super()._start()

        # initialize registry
        self.logger.info("Initializing registry...")
        self._init_registry()

        # initialize source
        self.logger.info("Initializing source...")
        self._init_source()

        self.logger.info("NL2LLMAgent initialization complete")

    def _init_registry(self):
        """Initialize the data registry."""
        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.logger.info(f"Creating DataRegistry with id={self.properties['data_registry.name']}, prefix={prefix}")
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix, properties=self.properties)
        self.logger.info("DataRegistry created successfully")

    def _init_source(self):
        """Initialize the source for the agent."""
        # initialize optional settings
        self.selected_source = None
        self.selected_source_protocol = None
        self.selected_source_protocol_variant = None

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
                    self.logger.info(f"selected source: {self.selected_source}")
                    self.logger.info(f"selected source protocol: {self.selected_source_protocol}")
                    self.logger.info(f"selected source protocol variant: {self.selected_source_protocol_variant}")
        else:
            ## discover llm sources
            scope = None
            sources = self._search_sources(scope=scope)
            self.logger.info(f"Found sources: {sources}")
            # return only the first available source
            if sources:
                self.selected_source = sources[0]
                source_properties = self.registry.get_source_properties(self.selected_source)
                if source_properties and 'connection' in source_properties:
                    self.selected_source_protocol = source_properties['connection']['protocol']
                    self.selected_source_protocol_variant = source_properties['connection'].get('protocol_variant', None)
                    self.logger.info(f"selected source: {self.selected_source}")
                    self.logger.info(f"selected source protocol: {self.selected_source_protocol}")
                    self.logger.info(f"selected source protocol variant: {self.selected_source_protocol_variant}")
                else:
                    self.logger.error(f"Source {self.selected_source} has no connection properties")
            else:
                self.logger.error("No sources found during discovery. Please check data registry configuration.")
                # Set a default source for now
                self.selected_source = "openai"
                self.selected_source_protocol = "openai"
                self.logger.info(f"Using default source: {self.selected_source}")

    def _search_sources(self, scope=None):
        """Search the data registry for sources that match the question.

        Parameters:
            scope: The scope to search data registry within. If None, searches all scopes.

        Returns:
            A list of source names that match the search criteria."""
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

    def get_properties(self, properties=None):
        """Get properties for the NL2LLM agent.
        Copied from RequestorAgent.get_properties().

        Parameters:
            properties: Optional properties dictionary to override agent properties. Defaults to None.

        Returns:
            A dictionary of merged properties.
        """
        merged_properties = {}

        # copy agent properties
        for p in self.properties:
            merged_properties[p] = self.properties[p]

        # override
        if properties is not None:
            for p in properties:
                merged_properties[p] = properties[p]

        return merged_properties

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process incoming messages and execute LLM queries.

        Parameters:
            message: The message to process.
            input: The input stream label.
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """

        if message.isEOS():
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')

            # get properties, overriding with properties provided
            properties = self.get_properties(properties=properties)

            # process the accumulated data
            if stream_data and len(stream_data) > 0:
                input_data = stream_data[0]

                # Only process if we have valid input data (not None, not empty)
                if input_data and input_data.strip() != "":
                    self.logger.info(f"Processing accumulated input: {input_data}")

                    # process the query
                    result = self.process_query(input_data, properties=properties)

                    # write result to output stream
                    if worker:
                        worker.write_data(result)
                else:
                    self.logger.info(f"Skipping processing for empty/null input: {input_data}")
            else:
                self.logger.info("No data accumulated in stream, skipping processing")

            if worker:
                worker.write_eos()

        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream', [])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            self.logger.info(f"Accumulating data: {data}")

            if worker:
                worker.append_data('stream', str(data))

        return None

    def process_query(self, question, properties=None):
        """Process a natural language query using the selected LLM source.

        Parameters:
            question: The natural language question to process.
            properties: Additional properties for processing.

        Returns:
            A dictionary containing the question, source, result, and any error encountered."""
        properties = self.get_properties(properties=properties)

        # Validate question - return None for empty/null questions
        if question is None or question == "" or question.strip() == "":
            self.logger.info(f"Skipping processing for empty/null question: {question}")
            return None

        # check if source is selected
        if self.selected_source is None:
            error = "No source selected. Please check data registry configuration."
            self.logger.error(error)
            return self._apply_filter({'question': question, 'source': None, 'result': None, 'error': error}, properties=properties)

        try:
            # initialize source if not already initialized
            if self.selected_source is None:
                self._init_source()

            # connect to the source
            source_connection = self.registry.connect_source(self.selected_source)

            # execute query
            self.logger.info(f"source: {self.selected_source}")
            self.logger.info(f"executing query: {question}")

            result = source_connection.execute_query(question, optional_properties={'context': properties.get('nl2llm_context', ""), 'attr_names': properties.get('nl2llm_attr_names', [])})

            self.logger.info("result: " + str(result))

            # apply output filters
            filtered_result = self._apply_filter({'question': question, 'source': self.selected_source, 'result': result, 'error': None}, properties=properties)

            return filtered_result

        except Exception as e:
            error = str(e)
            self.logger.error(f"Error executing query: {error}")

            # apply output filters
            filtered_result = self._apply_filter({'question': question, 'source': self.selected_source, 'result': None, 'error': error}, properties=properties)

            return filtered_result

    def _apply_filter(self, output, properties=None):
        """Apply output filters to the result.

        Parameters:
            output: The output dictionary containing question, source, result, and error.
            properties: Additional properties for processing.

        Returns:
            A filtered output based on the specified output filters.
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
            message = {'question': question, 'source': source, 'result': result, 'error': error}
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
