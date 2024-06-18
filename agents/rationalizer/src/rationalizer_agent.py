###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/apicaller/')
sys.path.append('./lib/openai/')
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

###### Blue
from agent import Agent, AgentFactory
from api_agent import APIAgent
from session import Session
from openai_agent import OpenAIAgent


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class RationalizerAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "RATIONALIZER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        self.properties['openai.api'] = 'ChatCompletion'
        self.properties['openai.model'] = "gpt-3.5-turbo"
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'prompt'
        self.properties['output_path'] = '$.choices[0].text'
        self.properties['openai.stream'] = False
        self.properties['openai.max_tokens'] = 2000
        self.properties['openai.temperature'] = 0
        self.properties["output_path"] = "$.choices[0].message.content"
        self.properties["input_json"] = "[{\"role\":\"user\"}]"
        self.properties["input_context"] = "$[0]"
        self.properties["input_context_field"] = "content"
        self.properties["input_field"] = "messages"
        self.properties["input_template"] = '''Let's assume a recommender system which recommends the next job position a candidate may pursue as their next job based on the candidate's current skill set and years of experience with each skill. 

                Consider a candidate with the current job position:\n{title} \nand current skills with months of experience: {resume_skills}

                Following is the recommended next job position: \n{top_title_recommendation}
                \nThis job requires the following skills with a corresponding average months of experience: {top_title_skills}

                Now provide rationale for why "{top_title_recommendation}" has been recommended as the next position the candidate should pursue.
                '''
        
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['RECORDER']
        listeners['excludes'] = [self.name]

        # rationalizer config
        self.properties['requires'] = ['title', 'top_title_recommendation', 'resume_skills', 'top_title_skills']

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):    
        if label == 'EOS':
            if worker:
                processed = worker.get_agent_data('processed')
                if processed:
                    return 'EOS', None, None
            return None
                
        elif label == 'BOS':
            pass
        elif label == 'DATA':
            # check if a required variable is seen
            requires = properties['requires']

            required_recorded = True
            for require in requires:
                # check if require is in session memory
                if worker:
                    v = worker.get_session_data(require)
                    logging.info("variable: {} value: {}".format(require, v))
                    if v is None:
                        required_recorded = False 
                        break

            if required_recorded:
                if worker:
                    processed = worker.get_agent_data('processed')
                    if processed:
                        return None

                    for require in requires:
                        logging.info('checking {}'.format(require))
                        properties[require] = worker.get_session_data(require)

                    
                    #### call service to compute

                    message = self.create_message("", properties=properties)

                    logging.info("::::: Message :::::")
                    logging.info(self.properties["input_template"])
                    # serialize message, call service
                    m = json.dumps(message)
                    r = self.call_service(m)

                    response = json.loads(r)

                    # create output from response
                    output_data = self.create_output(response)
                    logging.info(output_data)

                     # set processed to true
                    worker.set_agent_data('processed', True)

                    # output to stream
                    return "DATA", output_data, "str", True
    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="RATIONALIZER", type=str)
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
        
        af = AgentFactory(agent_class=RationalizerAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = RationalizerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = RationalizerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()



