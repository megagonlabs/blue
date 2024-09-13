###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')

###### 
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm


###### dspy
import dspy

###### Blue
from agent import Agent, AgentFactory
from session import Session
from message import Message, MessageType, ContentType, ControlCode


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################    
class ExtractOperator(dspy.Signature):
    """Given a natural language text, tag the named entities with [MEN] and [/MEN]"""

    text = dspy.InputField(desc="natural language text without entity annotations")
    annotated_text = dspy.OutputField(desc="natural language text with annotations", prefix='')

class DSPyAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "DSPY"
        super().__init__(**kwargs)


    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        self.dspy_operator = dspy.Predict(ExtractOperator)
        llm = dspy.OpenAI(model=self.properties["model"], api_key=self.properties["OPENAI_API_KEY"])

        dspy.settings.configure(lm=llm, rm=None)

        output = self.dspy_operator(text="testing: data scientist positions at Google")
        logging.info("ANNOTATIONS:" + str(output.annotated_text))
        logging.info("TESTING-----")

    def _initialize_properties(self):
        super()._initialize_properties()

        # dspy properties 
        self.properties["model"] = "gpt-4o"

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if message.isEOS():
            # compute stream data
            stream_data = ""
            if worker:
                stream_data = " ".join(worker.get_data('stream_data'))

            ### get budget
            budget = worker.session.get_budget()
            logging.info("BUDGET:")
            logging.info(json.dumps(budget, indent=3))

            ### apply dspy operator
            llm = dspy.OpenAI(model=self.properties["model"], api_key=self.properties["OPENAI_API_KEY"])
            dspy.settings.configure(lm=llm, rm=None)
            output = worker.agent.dspy_operator(text=stream_data)

            ### update budget
            worker.session.set_budget_use(cost=0.3)
            
            # output to stream
            return output.annotated_text
        
        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream_data',[])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            logging.info(data)
            
            if worker:
                worker.append_data('stream_data', data)
    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="DSPY", type=str)
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
        
        af = AgentFactory(_class=DSPyAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = DSPyAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = DSPyAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()



