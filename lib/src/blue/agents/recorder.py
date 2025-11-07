###### Parsers, Formats, Utils
import logging


###### Blue
from blue.agent import Agent
from blue.stream import ContentType
from blue.utils import json_utils


############################
### Agent.RecorderAgent
#
class RecorderAgent(Agent):
    """An agent that records specific data from input streams based on configured queries, scanning JSON data.
    The recorded data is stored in session variables for later use by other agents or processes.

    Properties (in addition to Agent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `records`       | `list of dict`        | `[]`       | List of record configurations, each containing: `variable` (name of the session variable to store the result), `query` (the jsonpath query to execute on the input data), and `single` (boolean indicating if a single result is expected). |

    Inputs:
    - `DEFAULT`: The JSON input stream to process and query records.

    Outputs:
    None.
    
    """

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "RECORDER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        """Initialize default properties for the recorder agent, setting it as an aggregator with specific recording configurations."""
        super()._initialize_properties()

        # recorder is an aggregator agent
        self.properties['aggregator'] = True
        self.properties['aggregator.eos'] = 'NEVER'

        # recorder config
        records = []
        self.properties['records'] = records
        records.append({"variable": "all", "query": "$", "single": True})

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the recorder agent, listening to streams tagged as JSON."""
        self.add_input("DEFAULT", description="JSON input stream to process and query records", includes=["JSON"])

    def _initialize_outputs(self):
        """Initialize outputs for the recorder agent. No outputs by default."""
        # no output
        return

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the recorder agent, executing configured queries on JSON input data and storing results in session variables.

        Parameters:
            message: The incoming message to process.
            input: The input stream name. Defaults to "DEFAULT".
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a list of variable names that were set in the session.
        """
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
                        self.logger.info('Executing query {query}'.format(query=query))
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
