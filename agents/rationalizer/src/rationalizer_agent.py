###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/shared/')

###### 
import time
import argparse
import logging
import time
import uuid
import random
# import openai

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent
from api_agent import APIAgent
from session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class RationalizerAgent(APIAgent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("OPENAI", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        self.properties['openai.service'] = "ws://localhost:8003"

        self.properties['openai.api'] = 'ChatCompletion'
        self.properties['openai.model'] = "gpt-3.5-turbo"
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'prompt'
        self.properties['output_path'] = '$.choices[0].text'
        self.properties['openai.stream'] = False
        self.properties['openai.max_tokens'] = 50
        self.properties['openai.temperature'] = 0
        self.properties["output_path"] = "$.choices[0].message.content"
        self.properties["input_json"] = "[{\"role\":\"user\"}]"
        self.properties["input_context"] = "$[0]"
        self.properties["input_context_field"] = "content"
        self.properties["input_field"] = "messages"
        self.properties["input_template"] = '''Let's assume a recommender system which recommends a ranked list of job positions that a candidate may pursue as their next job based on the candidate's current skill set and years of experience with each skill. The ranked list is provided in the order of most relevant to least relevant job. 

                Consider a candidate with the current job position:\n{title} \nand current skills with years of experience: {resume_skills}

                Following is the recommended ranked list of next job positions: \n{title_recommendation}
                \nThis job requires the following skills with a corresponding average years of experience: {job_skills}

                Now provide rationale for why "{title_recommendation}" has been recommended as the next position the candidate should pursue. Also, provide rationale for why the other recommended job positions are lower in the ranked list.
                '''
        
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['RECORDER']
        listeners['excludes'] = [self.name]

        # rationalizer config
        self.properties['requires'] = ['title', 'title_recommendation', 'resume_skills', 'job_skills']

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):    
        if label == 'EOS':
            pass
                
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
                    for require in requires:
                        logging.info('checking {}'.format(require))
                        properties[require] = worker.get_session_data(require)[0]

                    
                    #### call service to compute

                    message = self.create_message("", properties=properties)

                    # serialize message, call service
                    m = json.dumps(message)
                    r = self.call_service(m)

                    response = json.loads(r)

                    # create output from response
                    output_data = self.create_output(response)
                    logging.info(output_data)
                    return output_data
    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
 
    args = parser.parse_args()

    session = None
    a = None

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.session:
        # join an existing session
        session = Session(args.session)
        a = RationalizerAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = RationalizerAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = RationalizerAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()



