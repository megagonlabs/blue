###### Parsers, Formats, Utils
import logging
import json
import pydash

###### WebSockets
from websocket import create_connection

###### Blue
from blue.agent import Agent
from blue.stream import Stream, ControlCode
from blue.utils import json_utils


#######################
class ObserverAgent(Agent):
    """
    An agent that observes all messages in a session and logs them or sends them to a specified output.
    Used primarily internally for Web UI.

    Properties (in addition to Agent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `output`         | `dict`                | `{}`       | Output configuration. If 'type' is 'websocket', messages are sent to the specified websocket URL. |
    | `debug_mode`     | `bool`                | `False`    | If True, hidden messages (with metadata tag HIDDEN) are also sent to the output. |

    Inputs:
    None

    Outputs:
    None
    """

    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "OBSERVER"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # observer is not instructable
        self.properties['instructable'] = False

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the observer agent, by default observe all streams."""
        self.add_input("DEFAULT", description="all messages", includes=[".*"])

    def _initialize_outputs(self):
        """Initialize outputs for the observer agent. No outputs by default."""
        pass

    def response_handler(self, stream, message={}):
        try:
            output = pydash.objects.get(self.properties, 'output', {})
            is_hidden = pydash.objects.get(message, 'metadata.tags.HIDDEN', False)
            debug_mode = pydash.objects.get(self.properties, 'debug_mode', False)
            if output.get('type') == "websocket":
                if is_hidden and not debug_mode:
                    return
                ws = create_connection(output.get("websocket"))
                ws.send(json.dumps(message))
                ws.close()
            else:
                self.logger.info("{} : {}".format(stream, message))
        except Exception as exception:
            self.logger.error("{}: {}".format(stream, exception))

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        """Process messages for the observer agent, logging or sending them to a specified output.

        Parameters:
            message: The message to process.
            input: The input stream label.
            properties: Additional properties for processing.
            worker: The worker handling the processing.

        Returns:
            None or a response message.
        """
        mode = None
        if 'output' in properties:
            mode = properties['output'].get('mode', 'batch')

        id = message.getID()
        stream = message.getStream()

        message_json = json.loads(message.toJSON())
        label = message_json["label"]
        contents = message_json["contents"]
        content_type = message_json["content_type"]
        if content_type == 'JSON':
            contents = json.loads(contents)

        stream_metadata = Stream(cid=stream, properties=properties).get_metadata()
        base_message = {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": properties["session_id"],
            "connection_id": properties["connection_id"],
            "message": {"label": label, "contents": contents, "content_type": content_type},
            "stream": stream,
            "metadata": stream_metadata,
            "mode": mode,
            "timestamp": int(id.split("-")[0]),
            "order": int(id.split("-")[1]),
            "id": id,
        }
        if message.isEOS():
            # compute stream data
            if worker:
                if mode == 'batch':
                    data = worker.get_data(stream)
                    stream_dtype = worker.get_data(f'{stream}:content_type')
                    if stream_dtype == 'json' and data is not None:
                        try:
                            self.response_handler(
                                stream=stream,
                                message={
                                    **base_message,
                                    "message": {**base_message['message'], "label": "DATA", "contents": [json.loads(json_data) for json_data in data], "content_type": 'JSON'},
                                },
                            )
                        except Exception as exception:
                            self.logger.error("{} : {}".format(stream, exception))
                    else:
                        if len(data) > 0:
                            self.response_handler(
                                stream=stream,
                                message={**base_message, "message": {**base_message['message'], "label": "DATA", "contents": [map(str, data)], "content_type": 'STR'}},
                            )
                elif mode == 'streaming':
                    self.response_handler(stream=stream, message=base_message)
        elif message.isBOS():
            # init stream to empty array
            if worker:
                if mode == 'batch':
                    worker.set_data(stream, [])
                elif mode == 'streaming':
                    self.response_handler(stream=stream, message=base_message)
        elif message.isData():
            # store data value
            data = message.getData()

            if worker:
                if mode == 'batch':
                    worker.set_data(f'{stream}:content_type', content_type)
                    worker.append_data(stream, str(data))
                elif mode == 'streaming':
                    self.response_handler(stream=stream, message=base_message)
        elif message.getCode() in [ControlCode.CREATE_FORM, ControlCode.UPDATE_FORM, ControlCode.CLOSE_FORM, ControlCode.PROGRESS]:
            # interactive messages
            self.response_handler(stream=stream, message=base_message)

        return None
