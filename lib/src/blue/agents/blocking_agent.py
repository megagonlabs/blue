###### Parsers, Formats, Utils
import logging
import json
import threading

###### Blue
from blue.agent import Agent, AgentFactory
from blue.stream import Message
from blue.session import Session


############################
### Agent.BlockingAgent
#
class BlockingAgent(Agent):
    """
    An agent that waits for multiple inputs before processing to be present and then processes them together.
    It can be configured to wait for a list of input streams before proceeding with its processing logic.

    This is an experimental implementation and may be subject to changes in future releases.

    Properties (in addition to Agent properties):
    ----------
    | Name                 | Type                 | Default | Description |
    |----------------------|----------------------|----------|-------------|
    | `wait_for_inputs`    | `list of str`        | `['DEFAULT']` | List of input stream labels that the agent should wait for before processing. |
    | `include_extra_input` | `bool`               | `True`   | If true, any extra input streams not specified in `wait_for_inputs` will also be included in the processing logic. |

    Inputs:
    - `DEFAULT`: The main input stream where the agent receives data.

    Outputs:
    - `DEFAULT`: The output stream where the processed data is sent.
    """

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "BLOCKING_AGENT"
        super().__init__(**kwargs)

        self.lock = threading.Lock()
        self.agent_name = kwargs['name']

        # get wait_for list
        val = self.properties.get("wait_for_inputs", ["DEFAULT"])
        if not isinstance(val, list):
            val = [val]  # wrap single values into a list
        self.wait_for_inputs = [str(item) for item in val]

        # set shared memory to flag input
        self.inputs_received = {item: False for item in self.wait_for_inputs}

        # if true, extra input not specified in the wait_for list will be included in the
        # processing logic. Note the extrac input could have incomplete streams.
        self.include_extra_input = bool(self.properties.get("include_extra_input", True))

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the blocking agent."""
        self.add_input("DEFAULT", description="input text")

    def _initialize_outputs(self):
        """Initialize outputs for the blocking agent."""
        self.add_output("DEFAULT", description="echoing or combining input")

    def process_logic(self, input_dict, worker):
        # echoing all input, rewrite with specific logic in inherited classes.
        result = f"Agent {self.agent_name} got" + str(input_dict)
        return result

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the blocking agent, waiting for all specified inputs before proceeding calling process_logic() when all inputs are gathered.

        Parameters:
            message: The message to process.
            input: The input stream label.
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """
        if message.isEOS():

            try:
                with self.lock:
                    from_agent = input.strip("FROM_")
                    if from_agent in self.inputs_received:
                        self.inputs_received[from_agent] = True
                    ready_to_process = all(self.inputs_received.values())

                    logging.info(f"Agent {self.agent_name} got INPUT {input}, ready to process:{ready_to_process}, inputs:{str(self.inputs_received)} ")

                    if ready_to_process:
                        input_dict = worker.get_all_data()
                        # remove extrat input per configuration
                        # concatenate data in stream
                        if not self.include_extra_input:
                            input_dict = {k: ' '.join(v) for k, v in input_dict.items() if k.strip("FROM_") in self.wait_for_inputs}
                        else:
                            input_dict = {k: ' '.join(v) for k, v in input_dict.items()}

                        return [self.process_logic(input_dict, worker), Message.EOS]

            except Exception as e:
                logging.error(f"Agent {self.agent_name} execution failed: {e}")
                return [
                    f"Agent {self.agent_name} execution failed: {e}",
                    Message.EOS,
                ]

        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data(f'{input}', [])
        elif message.isData():
            # store data value
            data = message.getData()

            if worker:
                worker.append_data(f'{input}', data)

        return None
