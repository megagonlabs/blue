

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

###### Blue
from agent import Agent, AgentFactory
from session import Session


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class JobSearchAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "JOBSEARCH"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['Recorder']
        listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties['tags'] = ['JSON']

    def create_jobs_list(self, jobs):
        
        top_elements = []
        jobs_list_ui = {
            "type": "VerticalLayout",
            "elements": top_elements
        }

        jobs_form = {
            "schema": {},
            "uischema": jobs_list_ui,
        }
        
        # Add title
        top_elements.append({
            "type": "Label",
            "label": "Jobs",
            "props": {
                "large": True
            }
        })

        for job in jobs:
            job_details = []

            job_element = {
                "type": "HorizontalLayout",
                "elements": job_details
            }

            # add job title
            job_details.append({
                "type": "Label",
                "label": job['title']
            })
            # add company
            job_details.append({
                "type": "Label",
                "label": job['company']
            })
            # add apply button
            job_details.append({
                "type": "Button",
                "label": "Apply",
                "props": {
                    "nameId": "apply",
                    "large": False
                }
            })

            # add to list
            top_elements.append(job_element)
            
        return jobs_form


    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):

        if label == 'DATA':
            # check if title is recorded
            variables = data
            variables = set(variables) 

            if 'name' in variables:
                if worker:
                    name = worker.get_session_data('name')


                    logging.info("recommended jobs with name: {name}".format(name=name))
                
                    # do job search
                    jobs = [
                        {'title': 'Sr. Research Engineer', 'company': 'Megagon Labs', 'link': 'https://megagon.ai/jobs/research-engineer/'},
                        {'title': 'Research Scientist', 'company': 'Megagon Labs', 'link': 'https://megagon.ai/jobs/research-scientist/'},
                    ]
                    
                    jobs_form = self.create_jobs_list(jobs)
                    return ("INTERACTION", {"type": "JSONFORM", "content": jobs_form}, "json", False)
                    
                    # output to stream
                    # return "DATA", json.dumps({ "jobs": results }, indent=3), "str", True
                    # return "DATA", { "jobs": results }, "json", True
        
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="JOBSEARCH", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str, default='JOBSEARCH')
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
        
        af = AgentFactory(agent_class=JobSearchAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(args.session)
            a = JobSearchAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            a = JobSearchAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()



