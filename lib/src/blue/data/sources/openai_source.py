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


###### Communication
from websockets.sync.client import connect

###### Source specific libs
import requests

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

###############
### OpenAISource

class OpenAISource(DataSource):
    PROMPT = """
Your task is to process a natural language query and return the results in JSON format.
The response should be a valid JSON array containing the requested information.

Here are the requirements:
- There might be optional context provided for domain knowledge. Use it to assist the query.
- There might be specificed attr_names, which are the attributes of the objects in the output.
- The output should be a JSON array of objects. Each element is a JSON object with proper attribute value pairs.
- Each object should contain the requested information in a structured format
- When interpreting the query, use any additional context provided.
- The response should be well-formatted and easy to parse
- Output the JSON directly. Do not generate explanation or other additional output.

Query: ${query}

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

        # io related properties
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": PROMPT,
        "output_path": "$.choices[0].message.content",

        # service related properties
        "service.prefix": "openai",
        # "api.service": "ws://localhost:8001",

        # output transformations
        "output_transformations": [
            {
                "transformation": "replace",
                "from": "```",
                "to": ""
            },
            {
                "transformation": "replace",
                "from": "json",
                "to": ""
            }
        ],
        "output_strip": True,
        "output_cast": "json"
    }

    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # source protocol 
        self.properties['protocol'] = "openai"

        # Initialize default properties
        for key in OpenAISource.PROPERTIES:
            self.properties[key] = OpenAISource.PROPERTIES[key]

    ###### connection
    def _connect(self, **connection):
        self.host = connection.get('host')
        self.port = connection.get('port')
        # logging.debug(f"OpenAI source connected to {self.host}:{self.port}")
        return None

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

    def fetch_database_collection_schema(self, database, collection):
        return {}

    ######### format prompt
    def _format_prompt(self, query, context:str=None, attr_names:list=None):
        """Format the prompt with the query and context.
        Context is just a placeholder for additional information.
        """
        prompt = self.properties['input_template']
        context_str = "\n".join(context) if context else ""
        # attr_names is a list of strings
        attr_names_str = "\n".join([f"- {name}" for name in attr_names]) if attr_names else ""
        return prompt.format(query=query, context=context_str, attr_names=attr_names_str)

    ######### apply transformations
    def _apply_transformations(self, content:str):
        """Apply output transformations to the content.
        Transformations are applied in the order they are defined.
        """
        if not content:
            return content

        # strip
        if self.properties.get('output_strip', True):
            logging.info("output_strip")
            content = content.strip()

        # re transformations
        if self.properties.get('output_transformations', []):
            logging.info("output_transformations")
            transformations = self.properties.get('output_transformations', [])
            for transform in transformations:
                if transform['transformation'] == 'replace':
                    content = content.replace(transform['from'], transform['to'])
                elif transform['transformation'] == 'sub':
                    content = re.sub(transform['from'], transform['to'], content)
        return content

    def _parse_response(self, response:list):
        """Parse and validate the response content.
        """
        try:
            # Apply transformations
            content = self._apply_transformations(response)
            
            # Parse JSON
            if self.properties.get('output_cast') == 'json':
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        return parsed
                    else:
                        return [parsed]
                except json.JSONDecodeError:
                    return [{"content": content}]
            else:
                return [{"content": content}]
        except Exception as e:
            logging.error(f"Error parsing response: {str(e)}")
            return [{"error": str(e)}]
    
    def get_service_address(self):
        if 'api.service' in self.properties:
            service_address = self.properties['api.service']
        else:
            service_address = f"ws://{self.host}:{self.port}"
        return service_address
    
    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """Execute a natural language query against OpenAI service synchronously.
        """
        context = optional_properties.get('context', '')
        attr_names = optional_properties.get('attr_names', [])
        
        # Format the prompt with query and context
        formatted_prompt = self._format_prompt(query, context, attr_names)
        
        # Prepare API payload
        payload = {
            "api": self.properties['openai.api'],
            "model": self.properties['openai.model'],
            "messages": [
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            "max_tokens": self.properties['openai.max_tokens'],
            "temperature": self.properties['openai.temperature'],
            "stream": self.properties['openai.stream']
        }

        try:
            with connect(self.get_service_address()) as websocket:
                logging.info("Sending to service: {data}".format(data=payload))
                payload_str = json.dumps(payload)
                websocket.send(payload_str) 
                message = websocket.recv()
                result = json.loads(message)
                content = result['choices'][0]['message']['content']
                logging.info("Received from service: {message}".format(message=message))
                return content
        except Exception as e:
            logging.error(f"Error executing OpenAI query: {str(e)}")
            return [{"error": str(e)}]
        
