###### Parsers, Formats, Utils
import logging
import pydash


###### Blue
from blue.agent import Agent
from blue.stream import Message, ControlCode

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")



#########################
### Agent.PresenterAgent
#
class PresenterAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "PRESENTER"
        super().__init__(**kwargs)

    def triggered(self, text, properties):
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
                        args = {
                            "form_id": form_id
                        }
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
                                stream=form_data_stream
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

