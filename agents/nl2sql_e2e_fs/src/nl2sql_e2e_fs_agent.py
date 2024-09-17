###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append('./lib/openai/')
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")
sys.path.append('./lib/data_registry/')

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
from openai_agent import OpenAIAgent
from data_registry import DataRegistry
from session import Session
from message import Message, MessageType, ContentType, ControlCode

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

NL2SQL_PROMPT = """Your task is to translate a natural language question into a SQL query based on a list of provided data sources.
For each source you will be provided with a list of table schemas that specify the columns and their types.

Here are the requirements:
- The output should be a JSON object with the following fields
  - "source": the name of the data source that the query will be executed on
  - "query": the SQL query that is translated from the natural language question
- The SQL query should be compatible with the schema of the datasource.
- Output the JSON directly. Do not generate explanation or other additional output.

Some example pairs of question and corresponding SQL query are provided based on similar problems:

Question: What are the codes corresponding to document types for which there are less than documents?
SQL: SELECT document_type_code FROM Documents GROUP BY document_type_code HAVING count(*)  <  3

Question: What are the names of all the video games and their types in alphabetical order?
SQL: SELECT gname ,  gtype FROM Video_games ORDER BY gname

Question: Which papers\' first author is affiliated with an institution in the country "Japan" and has last name "Ohori"? Give me the titles of the papers.
SQL: SELECT t3.title FROM authors AS t1 JOIN authorship AS t2 ON t1.authid  =  t2.authid JOIN papers AS t3 ON t2.paperid  =  t3.paperid JOIN inst AS t4 ON t2.instid  =  t4.instid WHERE t4.country  =  "Japan" AND t2.authorder  =  1 AND t1.lname  =  "Ohori"

Question: What is the total access count of documents that are of the most common document type?
SQL: SELECT sum(access_count) FROM documents GROUP BY document_type_code ORDER BY count(*) DESC LIMIT 1

Question: Show the distinct fate of missions that involve ships with nationality "United States"
SQL: SELECT DISTINCT T1.Fate FROM mission AS T1 JOIN ship AS T2 ON T1.Ship_ID  =  T2.Ship_ID WHERE T2.Nationality  =  "United States"


Data sources:
```
${sources}
```
Question: ${question}
Output:
"""

agent_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": NL2SQL_PROMPT,
    "openai.temperature": 0,
    "openai.max_tokens": 512,
    "listens": {
        "DEFAULT": {
            "includes": ["USER"],
            "excludes": []
        }
    }
}


#######################
class Nl2SqlE2EFSAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2SQL_E2E_FS"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)
        self.schemas = {}
        logging.info('<sources>' + json.dumps(self.registry.get_sources(), indent=2) + '</sources>')
        for source in self.registry.get_sources():
            properties = self.registry.get_source_properties(source)
            if 'connection' not in properties or properties['connection']['protocol'] != 'postgres':
                continue
            source_db = self.registry.connect_source(source)
            for db in self.registry.get_source_databases(source):
                db = db['name']
                # Note: collection refers to schema in postgres (the level between database and table)
                for collection in self.registry.get_source_database_collections(source, db):
                    collection = collection['name']
                    assert all('/' not in s for s in [source, db, collection])
                    key = f'/{source}/{db}/{collection}'
                    if 'sample' in key or 'template' in key:
                        continue
                    schema = source_db.fetch_database_collection_schema(db, collection)
                    self.schemas[key] = schema

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    def _format_schema(self, schema):
        res = []
        for table_name, record in schema['entities'].items():
            res.append({
                'table_name': table_name,
                'columns': record['properties']
            })
        return res

    def extract_input_params(self, input_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        sources = [{
            'source': key,
            'schema': self._format_schema(schema)
        } for key, schema in self.schemas.items()]
        sources = json.dumps(sources, indent=2)
        logging.info(f'<sources>{sources}</sources>')
        return {'sources': sources, 'question': input_data}

    def process_output(self, output_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        logging.info(f'output_data: {output_data}')
        response = output_data.replace('```json', '').replace('```', '').strip()
        key, query, result, error = None, None, None, None
        try:
            response = json.loads(response)
            key = response['source']
            query = response['query']
            _, source, db, collection = key.split('/')
            source_db = self.registry.connect_source(source)
            cursor = source_db._db_connect(db).cursor()
            # Note: collection refers to schema in postgres (the level between database and table)
            cursor.execute(f'SET search_path TO {collection}')
            cursor.execute(query)
            result = cursor.fetchall()
        except Exception as e:
            error = str(e)
        return {
            'source': key,
            'query': query,
            'result': result,
            'error': error
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="NL2SQL_E2E_FS", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    args = parser.parse_args()

    for i in range(10):
        print('qwer' * 100 + str(i))

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

        af = AgentFactory(_class=Nl2SqlE2EFSAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = Nl2SqlE2EFSAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = Nl2SqlE2EFSAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
