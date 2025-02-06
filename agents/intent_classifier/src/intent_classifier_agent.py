###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.agent import AgentFactory, AgentRegistry
from blue.agents.openai import OpenAIAgent
from blue.session import Session
from blue.stream import ControlCode
from blue.utils import string_utils, json_utils, uuid_utils

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

class IntentClassifierAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        logging.info('In Init Function===============================================')
        if 'name' not in kwargs:
            kwargs['name'] = "INTENT_CLASSIFIER"
        super().__init__(**kwargs)
    
    def process_output(self, output_data, properties=None):
        logging.info('Entered process_output')
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        logging.info(output_data)
        # get gpt plan as json
        plan = json.loads(output_data)
        logging.info('Plan:')
        logging.info(json.dumps(plan, indent=4))
        logging.info('========================================================================================================')

        return plan

def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        logging.info('Entered default_processor')
        stream = message.getStream()

        if message.isEOS():
            logging.info("MESSAGE EOS")
            # get all data received from stream
            stream = message.getStream()
            stream_data = ""
            if worker:
                stream_data = worker.get_data(stream)

            logging.info('Stream data')
            logging.info(stream_data)

            #### call api to compute, render interactive plan
            interactive_plan = self.handle_api_call(stream_data)
            logging.info('Output of handle_api_call' + str(interactive_plan))

            
        elif message.isBOS():
            logging.info("MESSAGE BOS")
            stream = message.getStream()
            # init stream to empty array
            if worker:
                worker.set_data(stream,[])
            pass
        elif message.isData():
            logging.info("MESSAGE DATA")
            # store data value
            data = message.getData()
            stream = message.getStream()

            logging.info("=====")
            logging.info(stream)
            logging.info(data)
            logging.info("=====")
            if worker:
                worker.append_data(stream, data)
        
        return None
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="INTENT_CLASSIFIER", type=str)
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

        af = AgentFactory(_class=IntentClassifierAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = IntentClassifierAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = IntentClassifierAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
