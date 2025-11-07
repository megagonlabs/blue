###### Parsers, Formats, Utils
import logging
import json

###### Blue
from blue.agent import Agent
from blue.stream import ContentType, Message
from blue.data.registry import DataRegistry


############################
### Agent.QueryExecutorAgent
#
class QueryExecutorAgent(Agent):
    """
    An agent that executes queries against a specified data source and database using the DataRegistry.
    The agent takes input in the form of JSON containing the source, database, and query to execute.

    Properties (in addition to Agent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `output_filters` | `list of str`        | `['all']` | List of output filters to apply to the query result (e.g., 'all', 'question', 'source', 'query', 'result', 'error'). |
    | `output_max_results` | `int`                | `None`  | Maximum number of results to return in the output. If not specified, all results are returned. |

    Inputs:
    - `DEFAULT`: The main input stream where the agent receives query requests in JSON format.

    Outputs:
    - `DEFAULT`: The output stream where the query results are sent, tagged as QUERY, RESULT, and HIDDEN.
    """

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "QUERYEXECUTOR"
        super().__init__(**kwargs)

    def _start(self):
        """Start the QueryExecutorAgent by initializing the data registry."""
        super()._start()

        # initialize registry
        self._init_registry()

    def _init_registry(self):
        """Initialize the data registry for the QueryExecutorAgent."""
        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix, properties=self.properties)

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the query executor agent."""
        self.add_input("DEFAULT", description="input query")

    def _initialize_outputs(self):
        """Initialize outputs for the query executor agent, tagged as QUERY, RESULT, and HIDDEN."""
        self.add_output("DEFAULT", description="query results", tags=["QUERY", "RESULT", "HIDDEN"])

    def execute_sql_query(self, path, query):
        """Execute a SQL query against the specified data source and database.

        Parameters:
            path: The data source path in the format 'PLATFORM:<platform_id>/<source>/<database>/<collection>'.
            query: The SQL query to execute.

        Returns:
            A dictionary containing the query results or an error message.
        """
        result = None
        question = None
        error = None
        try:
            # extract source, database, collection
            _, source, database, collection = path.split('/')
            # connect
            source_connection = self.registry.connect_source(source)
            # execute query
            result = source_connection.execute_query(query, database=database, collection=collection)
        except Exception as e:
            error = str(e)

        return {'question': question, 'source': path, 'query': query, 'result': result, 'error': error}

    def _apply_filter(self, output):
        """Apply output filters to the query result based on agent properties.

        Parameters:
            output: The output dictionary containing question, source, query, result, and error.

        Returns:
            The filtered output based on specified output filters.
        """
        output_filters = ['all']

        if 'output_filters' in self.properties:
            output_filters = self.properties['output_filters']

        question = output['question']
        source = output['source']
        query = output['query']
        result = output['result']
        error = output['error']

        # max results
        if "output_max_results" in self.properties and self.properties['output_max_results']:
            if isinstance(result, list):
                result = result[: self.properties['output_max_results']]

        message = None
        if 'all' in output_filters:
            message = {'question': question, 'source': source, 'query': query, 'result': result, 'error': error}
        elif len(output_filters) == 1:
            if 'question' in output_filters:
                message = question
            if 'source' in output_filters:
                message = source
            if 'query' in output_filters:
                message = query
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
            if 'query' in output_filters:
                message['query'] = query
            if 'result' in output_filters:
                message['result'] = result
            if 'error' in output_filters:
                message['error'] = error

        if message:
            return message

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the query executor agent, executing SQL queries based on input JSON data.

        Parameters:
            message: The message to process.
            input: The input stream label.
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """
        ##### Upon USER/Agent input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                # extract json
                input = " ".join(worker.get_data(stream))

                # self.logger.info("input: "  + input)

                if worker:
                    if input.strip() != '':
                        try:
                            data = json.loads(input)
                            path = data['source']
                            query = data['query']
                            output = self.execute_sql_query(path, query)

                            worker.write_data(self._apply_filter(output))

                        except:
                            print("Input is not JSON")
                            pass

                    worker.write_eos()

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
                    output = self.execute_sql_query(path, query)

                    return self._apply_filter(output)
                else:
                    # append to private stream data
                    if worker:
                        worker.append_data(stream, data)
