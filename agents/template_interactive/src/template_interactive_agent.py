###### Parsers, Formats, Utils
import argparse
import logging
import json
import pydash

###### Blue
from blue.agent import Agent, AgentFactory
from blue.session import Session
from blue.stream import ControlCode, Message

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

############################
### Agent.TemplateInteractiveAgent
#
class TemplateInteractiveAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "TEMPLATE_INTERACTIVE"
        super().__init__(**kwargs)

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
                        # gather all data, check if first_name is set
                        first_name = worker.get_stream_data("first_name.value", stream=form_data_stream)
                        last_name = worker.get_stream_data("last_name.value", stream=form_data_stream)
                        first_name_filled = not pydash.is_empty(pydash.strings.trim(first_name))
                        last_name_filled = not pydash.is_empty(pydash.strings.trim(last_name))

                        if not first_name_filled:
                            # TODO: REVISE THIS
                            # Is CALLOUT an UPDATE_FORM event?
                            # return (
                            #     "INTERACTION",
                            #     {
                            #         "type": "CALLOUT",
                            #         "content": {
                            #             "message": "First name cannot be empty.",
                            #             "intent": "warning",
                            #         },
                            #     },
                            #     "json",
                            #     False,
                            # )
                            pass
                        else:
                            # close form
                            args = {
                                "form_id": form_id
                            }
                            worker.write_control(ControlCode.CLOSE_FORM, args, output="FORM")

                            if first_name_filled and not last_name_filled:
                                args = {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"last_name": {"type": "string"}},
                                    },
                                    "uischema": {
                                        "type": "VerticalLayout",
                                        "elements": [
                                            {
                                                "type": "Label",
                                                "label": f"{first_name} who?",
                                                "props": {
                                                    "large": True,
                                                    "style": {
                                                        "marginBottom": 15,
                                                        "fontSize": "15pt",
                                                    },
                                                },
                                            },
                                            {
                                                "type": "HorizontalLayout",
                                                "elements": [
                                                    {
                                                        "type": "Control",
                                                        "label": "Last Name",
                                                        "scope": "#/properties/last_name",
                                                    }
                                                ],
                                            },
                                            {
                                                "type": "Button",
                                                "label": "Done",
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
                            elif first_name_filled and last_name_filled:
                                return [ "Hello, " + first_name + " " + last_name, Message.EOS ]
                    else:
                        path = data["path"]
                        timestamp = worker.get_stream_data(path + ".timestamp", stream=form_data_stream)
                        if timestamp is None or data["timestamp"] > timestamp:
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

                # compute and output to stream
                if pydash.is_equal(stream_message, "knock knock"):
                    args = {
                        "schema": {
                            "type": "object",
                            "properties": {"first_name": {"type": "string"}},
                        },
                        "uischema": {
                            "type": "VerticalLayout",
                            "elements": [
                                {
                                    "type": "Label",
                                    "label": "Who's there?",
                                    "props": {
                                        "large": True,
                                        "style": {
                                            "marginBottom": 15,
                                            "fontSize": "15pt",
                                        },
                                    },
                                },
                                {
                                    "type": "HorizontalLayout",
                                    "elements": [
                                        {
                                            "type": "Control",
                                            "label": "First Name",
                                            "scope": "#/properties/first_name",
                                        }
                                    ],
                                },
                                {
                                    "type": "Button",
                                    "label": "Done",
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
                logging.info(data)

                if worker:
                    worker.append_data(stream, data)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="TEMPLATE_INTERACTIVE", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.serve:
        platform = args.platform

        af = AgentFactory(
            _class=TemplateInteractiveAgent,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = TemplateInteractiveAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = TemplateInteractiveAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
