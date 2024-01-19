###### OS / Systems
import json
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")
sys.path.append("./lib/data_registry/")

import argparse
import csv
import itertools
import json
import logging
import random

###### Parsers, Formats, Utils
import re

######
import time
import uuid

import pandas

###### Blue
from agent import Agent
from data_registry import DataRegistry
from neo4j import GraphDatabase
from session import Session
from tqdm import tqdm

# import openai


# set log level
logging.getLogger().setLevel(logging.INFO)


#######################
class KnowledgGroundingAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__(
            "KNOWLEDGE",
            session=session,
            input_stream=input_stream,
            processor=processor,
            properties=properties,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        listeners = {}
        self.properties["listens"] = listeners
        listeners["includes"] = []
        listeners["excludes"] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties["tags"] = ["JSON"]

        # rationalizer config
        self.properties["requires"] = []  #'name', 'top_title_recommendation',]

        self.registry = DataRegistry("default")
        self.db_client = None
        self.db = None

    def resume_processing(self, profile):
        # get source for resume
        results = self.registry.search_records(
            keywords="resume",
            type="collection",
            scope=None,
            approximate=True,
            hybrid=False,
            page=0,
            page_size=10,
        )

        logging.info("List of collections with relevant information about resume.")
        logging.info(results)
        top_result = None
        for result in results:
            if result["name"] == "enriched_resume":
                top_result = result
        # establish connection to source
        if top_result:
            scope = top_result["scope"]
            logging.info("SCOPE")
            logging.info(type(scope))
            collection = top_result["name"]
            logging.info("Collection")
            logging.info(collection)
            source = scope.split("/")[1]
            database = scope.split("/")[2]
            logging.info(scope)
            logging.info(source)
            logging.info(database)
            source_connection = self.registry.connect_source(source)
            self.db_client = source_connection.connection
            self.db = self.db_client[database][collection]
            logging.info(self.db)

        else:
            # output to stream
            # return "DATA", {}, "json", True
            return {}

        db_cursor = self.db.find(
            {"profileId": profile}, {"extractions.skill.duration": 1}
        )
        logging.info(db_cursor)
        skills_duration_dict_ls = []
        for dbc in db_cursor:
            skills_duration_dict_ls.append(dbc)
        skills_duration_dict = skills_duration_dict_ls[0]["extractions"]["skill"][
            "duration"
        ]
        skills_duration_tuple = sorted(
            skills_duration_dict.items(), key=lambda x: x[1], reverse=True
        )
        skills_duration_current = {}
        for i, t in enumerate(skills_duration_tuple):
            if i > 2:
                break
            skill, duration = t
            skills_duration_current[skill] = duration

        return skills_duration_current

    def insight_processing(self, next_title):
        # get source for insights
        results = self.registry.search_records(
            keywords="hr insights",
            type="collection",
            scope=None,
            approximate=True,
            hybrid=False,
            page=0,
            page_size=10,
        )
        top_result = None
        for result in results:
            if result["name"] == "megagon_hr_insights":
                top_result = result
        # establish connection to source
        if top_result:
            scope = top_result["scope"]
            source = scope.split("/")[1]
            print(source)
            source_connection = self.registry.connect_source(source)
            print(source_connection)
            self.db_client = source_connection.connection
            print(self.db_client)
        else:
            # output to stream
            # return "DATA", {}, "json", True
            return {}

        # next_title = "hse officer"
        ## what does the insight DB have about a skill?
        title_query = """
            MATCH (j:JobTitle{{name: '{}'}})-[r:requires]->(s:Skill)
            RETURN s.name as skill, r.duration as duration
            ORDER BY r.duration DESC
            LIMIT 3
        """.format(
            next_title
        )
        print("Title query {}".format(title_query))
        result = self.db_client.run_query(title_query)
        print("Result {}".format(result))

        logging.info("Info about the next title")
        logging.info(result)

        return result

    def data_processing(self, worker):
        profile = self.properties["profile"]  # "1bv5ncadl2srsbmv" #1c1p1gdtu0l1m47s"
        # current_title = self.properties[]
        #     "title"
        # )  # "Software Engineer" # worker.get_session_data("title")
        skills_duration_current = self.resume_processing(profile)
        print("Skill Duration current {}".format(skills_duration_current))

        ### query insight db to get next title skiill recommendation
        next_title = self.properties["next_title"]  # "Senior Software Engineer"
        # worker.get_session_data("top_title_recommendation")
        skills_duration_next = self.insight_processing(next_title)
        print("Skill Duration Next {}".format(skills_duration_next))

        ret = {}
        ret["resume_skills"] = skills_duration_current
        ret["top_title_skills"] = skills_duration_next
        return ret

    def default_processor(
        self,
        stream,
        id,
        label,
        data,
        dtype=None,
        tags=None,
        properties=None,
        worker=None,
    ):
        if label == "EOS":
            if worker:
                processed = worker.get_agent_data("processed")
                if processed:
                    return "EOS", None, None
            return None

        elif label == "BOS":
            pass
        # elif label == 'DATA':
        # check if a required variable is seen
        requires = properties["requires"]
        logging.info("--------------")
        logging.info(requires)

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
                # processed = worker.get_agent_data("processed")
                # if processed:
                #     return None

                ret = self.data_processing(worker)

                # set processed to true
                worker.set_agent_data("processed", True)

                # output to stream
                return "DATA", ret, "json", True

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", type=str)
    parser.add_argument("--profile", type=str)
    parser.add_argument("--title", type=str)
    parser.add_argument("--next_title", type=str)
    parser.add_argument("--input_stream", type=str)
    parser.add_argument("--properties", type=str)

    args = parser.parse_args()

    session = None
    a = None

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.profile:
        properties["profile"] = args.profile

    if args.title:
        properties["title"] = args.title

    if args.next_title:
        properties["next_title"] = args.next_title

    kg = KnowledgGroundingAgent(properties=properties)
    ret = kg.data_processing("random")
    print(ret)
    logging.info(ret)

    # if args.session:
    #     # join an existing session
    #     session = Session(args.session)
    #     a = KnowledgGroundingAgent(session=session, properties=properties)
    # elif args.input_stream:
    #     # no session, work on a single input stream
    #     a = KnowledgGroundingAgent(
    #         input_stream=args.input_stream, properties=properties
    #     )
    # else:
    #     # create a new session
    #     a = KnowledgGroundingAgent(properties=properties)
    #     session = a.start_session()

    # # wait for session
    # session.wait()
