###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging
import os
import websockets
import asyncio
import re

###### Source specific libs
import requests

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema
from blue.utils import json_utils
from blue.utils.service_utils import ServiceClient

###############
### OpenAISource


class OpenAISource(DataSource, ServiceClient):
    PROMPT = """
Your task is to process a natural language query and return the results in JSON format.
The response should be a valid JSON array containing the requested information.

Here are the requirements:
- There might be optional context provided for domain knowledge. Use it to assist the query if provided and not empty.
- There might be specificed attr_names, which are the attributes of the objects in the output.
- The output should be a JSON array of objects. Each element is a JSON object with proper attribute value pairs.
- Each object should contain the requested information in a structured format
- When interpreting the query, use additional context provided if provided and not empty.
- Please try to return non-empty output. If the query is not clear, please use your best judgement to return a non-empty output.
- The response should be well-formatted and easy to parse
- Output the JSON directly. Do not generate explanation or other additional output.

Query: ${input}

Attr_names:
${attr_names}

Context:
${context}

Output:
"""

    PROPERTIES = {
        # openai related properties
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 4096,
        "openai.temperature": 0,
        # io related properties (used by requestor operator)
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # Initialize default properties
        for key in OpenAISource.PROPERTIES:
            self.properties[key] = OpenAISource.PROPERTIES[key]

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['protocol'] = 'openai'

    ###### connection
    def _connect(self, **connection):
        return {}

    def _disconnect(self):
        # OpenAI source doesn't require persistent connection
        return None

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### database
    def fetch_databases(self):
        return []

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

    ######### database/collection
    def fetch_database_collections(self, database):
        return []

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_entities(self, database, collection):
        return {}

    def fetch_database_collection_relations(self, database, collection):
        return {}


    def get_service_address(self, properties=None):
        service_address = f"ws://{self.host}:{self.port}"
        return service_address

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """Execute a natural language query against OpenAI service synchronously."""

        # Execute API Call
        return self.execute_api_call(query, properties=self.properties, additional_data=optional_properties)
