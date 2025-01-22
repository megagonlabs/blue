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

###### Postgres
import psycopg2

###### Blue
from agent import Agent, AgentFactory
from session import Session
from message import Message, MessageType, ContentType, ControlCode


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
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        self.properties['listens'] = listeners
        default_listeners['includes'] = ['Recorder']
        default_listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = {}
        default_tags = ['JSON']
        tags["DEFAULT"] = default_tags
        self.properties['tags'] = tags
        

    def create_jobs_list(self, jobs):

        top_elements = []
        jobs_list_ui = {"type": "VerticalLayout", "elements": top_elements}

        jobs_form = {
            "schema": {},
            "uischema": jobs_list_ui,
        }

        # Add title
        top_elements.append({"type": "Label", "label": "Jobs", "props": {"large": True}})

        top_elements.append({"type": "Label", "label": " ", "props": {"large": True, "style": {"marginBottom": 15, "fontSize": "12pt", "border-bottom": "thin solid gray"}}})

        for job in jobs:
            job_details = []

            job_element = {"type": "HorizontalLayout", "elements": job_details}

            # add job title
            job_details.append({"type": "Label", "label": job['title'], "props": {"style": {"width": "200px", "white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"}}})
            # add company
            job_details.append({"type": "Label", "label": job['company'], "props": {"style": {"width": "200px", "white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"}}})
            # add apply button
            job_details.append({"type": "Button", "label": "Apply", "props": {"action": "apply", "large": False}})

            # add to list
            top_elements.append(job_element)

        return jobs_form

    def search_jobs(self, title):
        user = self.properties['job_search.db.user']
        password = self.properties['job_search.db.pwd']
        host = self.properties['job_search.db.host']
        connection = psycopg2.connect(user='postgres', password=password, host=host)
        cursor = connection.cursor()
        cursor.execute("SELECT title, company FROM JOBS where lower(title) LIKE '%%" + title.lower() + "%%';")
        data = cursor.fetchall()
        results = []
        for datum in data:
            results.append({'title': datum[0], 'company': datum[1], 'link': 'http'})
        return results

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        if message.isData():
            # check if title is recorded
            data = message.getData()
            
            if 'desired_title' in data:
                title = data['desired_title']

                logging.info("recommended jobs with title: {title}".format(title=title))

    
                jobs = self.search_jobs(title)

                jobs_form = self.create_jobs_list(jobs)

                args = {
                    "schema": jobs_form["schema"],
                    "uischema": jobs_form["uischema"]
                }
                # write ui
                worker.write_control(ControlCode.CREATE_FORM, args, output="FORM")

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="JOBSEARCH", type=str)
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

        af = AgentFactory(_class=JobSearchAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = JobSearchAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = JobSearchAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
