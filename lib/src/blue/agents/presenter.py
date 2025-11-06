###### Parsers, Formats, Utils
import logging
import pydash


###### Blue
from blue.agent import Agent
from blue.stream import Message, ControlCode


#########################
### Agent.PresenterAgent
#
class PresenterAgent(Agent):
    """
    An agent that presents a form to the user when triggered by specific keywords in the input stream.
    The form schema and UI schema are defined in the agent's properties.
    The agent listens for specific triggers in the input stream and displays the form when triggered.
    The form data is collected and sent to a specified output stream when the user submits the form.

    Properties (in addition to Agent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `triggers`       | `list of str`        | `[]`       | List of keywords that trigger the form display when found in the input stream. |
    | `schema`         | `dict`                | `{}`       | The JSON schema defining the structure of the form to be presented. |
    | `form`           | `dict`                | `{}`       | The UI schema defining the layout and appearance of the form. |
    | `output`         | `str`                | `None`    | The output stream where the collected form data will be sent upon submission. If not specified, the data is returned as a message. |

    Inputs:
    - `DEFAULT`: The main input stream where the agent listens for trigger keywords.
    
    Outputs:
    - `DEFAULT`: The output stream where the collected form data is sent in structured format (JSON) upon form submission, tagged as JSON.
    - `FORM`: Control output stream for form UI interactions.

    """

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "PRESENTER"
        super().__init__(**kwargs)

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the presenter agent. By default, no specific inputs are defined."""
        return

    def _initialize_outputs(self):
        """Initialize outputs for the presenter agent, tagged as JSON."""
        self.add_output("DEFAULT", description="Form data in structured format (JSON)", tags=["JSON"])

    def triggered(self, text, properties):
        """Check if the input text contains any of the trigger keywords defined in properties.

        Parameters:
            text: The input text to check for triggers.
            properties: The properties dict containing trigger keywords.

        Returns:
            True if any trigger keyword is found in the text, False otherwise.
        """
        # if instructed, consider it triggered
        if 'instructable' in properties:
            if properties['instructable']:
                return True

        triggers = properties['triggers']
        for trigger in triggers:
            if trigger.lower() in text.lower():
                return True
        return False

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the presenter agent, displaying a form when triggered and collecting form data upon submission.

        Parameters:
            message: The incoming message to process.
            input: The input stream name. Defaults to "DEFAULT".
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """
        stream = message.getStream()

        if input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    form_id = data["form_id"]
                    action = data["action"]

                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")

                    # when the user clicked DONE
                    if action == "DONE":
                        # gather all data in the form from stream memory
                        schema = properties['schema']['properties'].keys()

                        form_data = {}
                        for element in schema:
                            form_data[element] = worker.get_stream_data(element + ".value", stream=form_data_stream)

                        # close form
                        args = {"form_id": form_id}
                        worker.write_control(ControlCode.CLOSE_FORM, args, output="FORM")

                        ### stream form data
                        # if output defined, write to output
                        if 'output' in self.properties:
                            output = self.properties['output']
                            worker.write_data(form_data, output=output)
                            worker.write_eos(output=output)
                        else:
                            return [form_data, Message.EOS]

                    else:
                        path = data["path"]
                        timestamp = worker.get_stream_data(path + ".timestamp", stream=form_data_stream)

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:
                            # save data into stream memory
                            worker.set_stream_data(
                                path,
                                {
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=form_data_stream,
                            )
        else:
            if message.isEOS():
                stream_message = ""
                if worker:
                    stream_message = pydash.to_lower(" ".join(worker.get_data(stream)))

                # check trigger condition, and output to stream form UI when triggered
                if self.triggered(stream_message, properties):
                    args = {
                        "schema": properties['schema'],
                        "uischema": {
                            "type": "VerticalLayout",
                            "elements": [
                                properties['form'],
                                {
                                    "type": "Button",
                                    "label": "Submit",
                                    "props": {
                                        "intent": "success",
                                        "action": "DONE",
                                        "large": True,
                                    },
                                },
                            ],
                        },
                    }
                    # write ui
                    worker.write_control(ControlCode.CREATE_FORM, args, output="FORM")

            elif message.isBOS():
                # init stream to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()

                if worker:
                    worker.append_data(stream, data)
