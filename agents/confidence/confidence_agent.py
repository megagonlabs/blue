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
from scipy.special import rel_entr

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
        self.properties['openai.max_tokens'] = 10

    def prediction_IntsructGPT(self, prompt):
        output = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature = self.properties['openai.temperature'],
                max_tokens = self.properties['openai.max_tokens'],
                logprobs = 100,
                n = 1
                )
        dict_out = output["choices"][0]["logprobs"]["top_logprobs"]
        return dict_out,  output["choices"][0]["text"]

class ConfidenceAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="Calibration", session=session, input_stream=input_stream, processor=processor, properties=calibration_properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.openai = OpenAIAgent(session=session, input_stream=input_stream, properties=properties)


    def kl_cal(self, dict_o, dict_i):
        prob_o = [math.exp(dict_o[tok]) for tok in dict_o]/(sum([math.exp(dict_o[tok]) for tok in dict_o]))
        prob_i = [math.exp(dict_i[tok]) for tok in dict_i]/(sum([math.exp(dict_i[tok]) for tok in dict_i]))
        prob_o.sort()
        prob_i.sort() 

        return sum(rel_entr(prob_o, prob_i))


    def calculate_confidence(self, dict_initial, dict_instilled):
        avg_score  = 0.0
        num = 0
        for i in range(min(len(dict_initial), len(dict_instilled))):
            avg_score += self.kl_cal(dict_initial[i], dict_instilled[i])
            num +=1

        return avg_score/num

    def calibrated_prediction(self, sample):
        prompt_initial = "Answer the question. Question: {}. Answer:".format(sample)
        dict_initial, ans_initial = OpenAIAgent.prediction_IntsructGPT(prompt_initial) 

        prompt_instilled = 'Knowing that {}, answer the question. Question: {}. Answer:'.format(ans_initial, sample)
        dict_instilled, _ = OpenAIAgent.prediction_IntsructGPT(prompt_instilled)

        confidence = self.calculate_confidence(dict_initial, dict_instilled)
        return confidence


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