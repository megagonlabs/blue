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
import openai

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent
from session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class RationalizerAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("RATIONALIZER", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def default_processor(self, stream, id, event, value, properties=None, worker=None):
        def all_agents_present(worker, agents=[]):
            for agent in agents:
                try:
                    if not worker.get_agent_data(agent):
                        return False
                except:
                    return False
            return True
        
        openai_api_key = os.environ['OPENAI_API_KEY']
        openai_organization = os.environ['OPENAI_ORGANIZATION']
        openai.api_key = openai_api_key
        openai.organization = openai_organization 
        model_config = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0
        }
        if event == 'EOS':
            # compute stream data
            l = 0
            if worker:
                stream_name = stream.split(':')[0]
                if stream_name == "RESUME":
                    data = worker.get_data('stream')[0]
                    worker.set_agent_data("RESUME", data)

                elif stream_name == "NEXT_JOB":
                    data = worker.get_data('stream')[0]
                    worker.set_agent_data("NEXT_JOB", data)

                if all_agents_present(worker, ["RESUME", "NEXT_JOB"]):
                    resume = ' '.join(worker.get_agent_data("RESUME")[0])
                    next_job = ' '.join(worker.get_agent_data("NEXT_JOB")[0])
                    prompt = '''
                    Let's assume a recommender system which recommends a ranked list of job positions that a candidate may pursue as their next job based on the candidate's current skill set and years of experience with each skill. The ranked list is provided in the order of most relevant to least relevant job. 

                    Consider a candidate with the current job position:\n{}

                    Following is the recommended ranked list of next job positions: \n{}

                    Now provide rationale for why "Software Development Engineer-2" has been recommended as the next position the candidate should pursue. Also, provide rationale for why the other recommended job positions are lower in the ranked list.
                    '''.format(resume, next_job)
                    response = openai.ChatCompletion.create(messages = [{
                                                                "role": "user", "content": prompt
                                                            }], **model_config)
                                                           
                    time.sleep(4)
                    return response["choices"][0]["message"]["content"]
                
        elif event == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif event == 'DATA':
            # store data value
            logging.info(value)
            
            if worker:
                worker.append_data('stream', value)
    
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



