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

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent
from api_agent import APIAgent
from session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)


#######################
 ##### sample properties for different openai models
## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages"}'
calibration_properties = {
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages"
}


class OpenAIAgent(APIAgent):
    def __init__(self, name="OPENAI", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['openai.service'] = "ws://localhost:8003"

        self.properties['openai.api'] = 'Completion'
        # self.properties['openai.model'] = "text-davinci-003"
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'prompt'
        self.properties['output_path'] = '$.choices[0].text'
        self.properties['openai.stream'] = False
        self.properties['openai.temperature'] = 0.0
        self.properties['openai.max_tokens'] = 200

    def prediction_GPT4(self, prompt):

        completion = openai.ChatCompletion.create(
            model = "gpt-4",
            temperature = self.properties['openai.temperature'],
            max_tokens = self.properties['openai.max_tokens'],
            messages = [{"role": "user", "content": prompt}])

        out = completion["choices"][0]["message"]["content"]
        return out

    def prediction_IntsructGPT(self, prompt):
        output = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature = self.properties['openai.temperature'],
                max_tokens = self.properties['openai.max_tokens'],
                n = 1
                )
        out = output["choices"][0]["text"]
        return out

class CalibrationAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="Calibration", session=session, input_stream=input_stream, processor=processor, properties=calibration_properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.openai = OpenAIAgent(session=session, input_stream=input_stream, properties=properties)

    def calibrated_prediction(self, sample, model = "GPT-4"):
        prompt = '''Answer the question. Question: {}. Please first provide a short explanation of your evaluation, avoiding any potential bias and ensuring that minor changes to the input does not affect your judgment. Then, output the answer.
                    Output with the following format:
                    Evaluation evidence: <evaluation explanation here> 
                    Answer: <answer>'''.format(sample) 

        if model == "GPT-4":
            out = OpenAIAgent.prediction_GPT4(prompt)
        else:
            out = OpenAIAgent.prediction_IntsructGPT(prompt)

        ind_p = out.find('Answer')
        return out[ind_p:]


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
        a = CalibrationAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = CalibrationAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = CalibrationAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()