###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/openai/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/agent_registry')
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
from utils import json_utils
import copy 

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent
from api_agent import APIAgent
from session import Session
from openai_agent import OpenAIAgent
from agent_registry import AgentRegistry

# set log level
logging.getLogger().setLevel(logging.INFO)


## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["USER"],"excludes":[]},"tags": ["TRIPLE"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Examine the text below and identify a task plan  thatcan be fulfilled by various agents. Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:\n{input}",  "openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0}'
plannerGPT_properties = {
    "openai.api":"ChatCompletion",
    "openai.model":"gpt-4",
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages",
    "input_template": """
Examine the text below and identify a task plan  thatcan be fulfilled by various agents. Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:
{input}
""",
    "openai.temperature":0,
    "openai.max_tokens":1024,
    "openai.top_p":1,
    "openai.frequency_penalty":0,
    "openai.presence_penalty":0,
    "registry.name": "default",
    "listens": {
        "includes": ["USER"],
        "excludes": []
    },
    "tags": ["PLAN"],
}

class GPTPlannerAgent(OpenAIAgent):
    def __init__(self, name="GPTPLANNER", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name=name, session=session, input_stream=input_stream, processor=processor, properties=properties)

        logging.info("Using agent registry:" + self.properties['registry.name'])
        self.registry = AgentRegistry(self.properties['registry.name'])

        agents = self.registry.list_records()
        logging.info('Registry contents:')
        logging.info(json.dumps(agents, indent=4))

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in plannerGPT_properties:
            self.properties[key] = plannerGPT_properties[key]

    def process_output(self, output_data):
        logging.info(output_data)
        # get gpt plan as json
        gpt_plan = json.loads(output_data)
        logging.info('GPT Returned Plan:')
        logging.info(json.dumps(gpt_plan, indent = 4))
        logging.info('-------------------------')

        # extract, standardize json plan
        extracted_plan = self.extract_plan(gpt_plan)

        # search, find related agents
        searched_plan = self.search_plan(extracted_plan)
        logging.info('Plan Search Results:')
        logging.info(json.dumps(searched_plan, indent = 4))
        logging.info('-------------------------')

        # rank matched agents, return plan
        ranked_plan = self.rank_plan(searched_plan)

        # finalize plan
        final_plan = self.finalize_plan(ranked_plan)
        logging.info('Final Plan:')
        logging.info(json.dumps(final_plan, indent = 4))
        return output_data
            
    def finalize_plan(self, plan):
        agents = plan['agent'].values()
        for agent in agents:
            inputs = agent['input']
            outputs = agent['output']

            # delete matches, filtered matches
            del agent['matches']
            del agent['filtered_matches']
            
            # assign match to top matched agent
            top_match = agent['top_match']
            agent['match'] = top_match
            del agent['top_match']
            # copy metadata
            match_info = top_match['info']
            for key in match_info:
                top_match[key] = match_info[key]
            del top_match['info']

            # clean up input/output parameters
            matched_agent_scope = '/'+top_match['name']
            for ii in inputs:
                input = inputs[ii]
                input_matches = input['matches']
                filtered_input_matches = []
                for input_match in input_matches:
                    if input_match['scope'] == matched_agent_scope:
                        filtered_input_matches.append(input_match)
                input['matches'] =  filtered_input_matches
            for oi in outputs:
                output = outputs[oi]
                output_matches = output['matches']
                filtered_output_matches = []
                for output_match in output_matches:
                    if output_match['scope'] == matched_agent_scope:
                        filtered_output_matches.append(output_match)
                output['matches'] =  filtered_output_matches
        return plan

    def rank_plan(self, plan):
        agent_dict = {}
        # get more details on each agent, including inputs, outputs
        agents = plan['agent'].values()
        for agent in agents:
            matches = agent['matches']
            for match in matches:
                name = match['name']
                if 'name' in agent_dict:
                    continue
                agent_info = self.registry.get_agent(name)
                agent_dict[name] = agent_info 
        ### rank each agent in the plan by score of agents, inputs, outputs
        # verify input/outputs 
        for agent in agents:
            matches = agent['matches']
            inputs = agent['input']
            outputs = agent['output']
            filtered_matches = []
            agent['filtered_matches'] = filtered_matches
            for match in matches:
                name = match['name']
                if name in agent_dict:
                    agent_info = agent_dict[name]
                    # create copy for agent in plan, set score from search
                    agent_info_copy = copy.deepcopy(agent_info)
                    match['info'] = agent_info_copy
                    # gather required agent inputs, outputs from registry record
                    agent_inputs = set()
                    agent_outputs = set()
                    contents = agent_info_copy['contents']
                    for pi in contents:
                        content = contents[pi]
                        if content['type'] == 'input':
                            content['matches'] = []
                            agent_inputs.add(pi)
                        elif content['type'] == 'output':
                            content['matches'] = []
                            agent_outputs.add(pi)
                    # check if number of inputs and outputs match
                    if len(inputs) != len(agent_inputs):
                        continue
                    if len(outputs) != len(agent_outputs):
                        continue 
                    # check agent has a matching parameter in search results for each input in planned agent
                    all_matched = True
                    for ii in inputs:
                        input = inputs[ii]
                        input_matches = input['matches']
                        # subset results for agent
                        matched = False
                        for input_match in input_matches:
                            if input_match['scope'] == '/' + name:
                                input_copy = copy.deepcopy(input)
                                del input_copy['matches']
                                input_copy['score'] = input_match['score']
                                contents[input_match['name']]['matches'].append(input_copy)
                                matched = True 
                        if not matched:
                            all_matched = False
                            break
                    # skip if an input from plan didn't match any from agent input parameters
                    if not all_matched:
                        continue
                    # check agent has a matching parameter in search results for each output in planned agent
                    all_matched = True
                    for oi in outputs:
                        output = outputs[oi]
                        output_matches = output['matches']
                        # subset results for agent
                        matched = False
                        for output_match in output_matches:
                            if output_match['scope'] == '/' + name:
                                output_copy = copy.deepcopy(output)
                                del output_copy['matches']
                                output_copy['score'] = output_match['score']
                                contents[output_match['name']]['matches'].append(output_copy)
                                matched = True 
                        if not matched:
                            all_matched = False
                            break
                    # skip if an output from plan didn't match any from agent output parameters
                    if not all_matched:
                        continue
                    # check if agent from registry has matches for all parameters
                    contents = agent_info_copy['contents']
                    all_matched = True
                    for pi in contents:
                        content = contents[pi]
                        if len(content['matches']) == 0:
                            all_matched = False
                    if not all_matched:
                        continue 
                    # TODO: Determine optimum mapping between planned agent parameters and registry agent parameters
                    # Compute total score 
                    total_score = float(match['score'])
                    contents = agent_info_copy['contents']
                    for pi in contents:
                        content = contents[pi]
                        # After optimization only one match left 
                        total_score = total_score * float(content['matches'][0]['score'])
                    match['total_score'] = total_score
                # add to filtered matches
                filtered_matches.append(match)
            # sort by total_score
            filtered_matches.sort(key=lambda match: match['total_score'])
            # select top
            if len(filtered_matches) > 0:
                agent['top_match'] = filtered_matches[0]
        return plan


    def search_plan(self, plan):
        agents = plan['agent'].values()
        for agent in agents:
            # search registry 
            name = agent['name']
            description = agent['description']

            # agents
            keywords = name + " " + description
            matches = self.registry.search_records(keywords, type='agent', approximate=True, page_size=10)
            agent['matches'] = matches

            # inputs
            inputs = agent['input'].values()
            for input in inputs:
                name = input['name']
                description = input['description']

                keywords = name + " " + description

                matches = self.registry.search_records(keywords, type='input', approximate=True, page_size=10)
                input['matches'] = matches


            # outputs
            outputs = agent['output'].values()
            for output in outputs:
                name = output['name']
                description = output['description']

                keywords = name + " " + description

                matches = self.registry.search_records(keywords, type='output', approximate=True, page_size=10)
                output['matches'] = matches

        return plan

    def extract_plan(self, data):
        plan = {}
        self._extract_plan(data, plan)
        self._clean_plan(plan)
        return(plan)

    def _extract_plan(self, data, plan, prefix=""):
        if type(data) == list:
            for i in range(len(data)):
                self._extract_plan(data[i], plan, prefix=prefix + '.' + str(i))
        elif type(data) == dict:
            for k in data:
                self._extract_plan(data[k], plan, prefix=prefix + '.' + k)
        else:
            if data:
                path = self._extract_path(prefix)
                self._set_plan_data(path, data, plan)

    def _extract_path(self, prefix):
        scope = []
        indices = []
        sp = prefix.split('.')
        for spi in sp:
            n = None
            try:
                n = int(spi)
            except:
                n = None
            if spi == '':
                continue
            elif n is not None:
                indices.append(n)
            elif spi.find('agent') > -1:
                scope.append('agent')
            elif spi.find('input') > -1:
                scope.append('input')
            elif spi.find('output') > -1:
                scope.append('output')
            else:
                if len(scope) > 0:
                    indices.append(spi)
        path = ''
        for s,i in zip(scope, indices[:-1]):
            path = path + str(s) + '['+ str(i)+ ']' + '.'
        if len(indices) > 0:
            path = path + indices[-1]
        return path
          
      
    def _set_plan_data(self, path, value, plan):
        p = path.split('.')
        scope = plan
        for pi in p[:-1]:
            s = pi.replace(']','').replace('[','.').split('.')
            ss = s[0]
            si = s[1]
            if ss in scope:
                scope = scope[ss]
            else:
                scope[ss] = {}
                scope = scope[ss]
            ndx = si
            is_number = None
            try:
                is_number = int(si)
            except:
                is_number = None
            if is_number is None:
                ndx2p = {}
                if '_ndx2p' in scope:
                    ndx2p = scope['_ndx2p']
                else:
                    scope['_ndx2p'] = ndx2p
                npp = str(p[:-1])
                ndx = len(scope)
                if npp in ndx2p: 
                    ndx = ndx2p[npp]
                else:
                    ndx2p[npp] = ndx
            if ndx in scope:
                scope = scope[ndx]
            else:
                scope[ndx] = {}
                scope = scope[ndx]
                if is_number is None:
                    scope['name'] = si
        key = p[-1]   
        scope[key] = value
       

    def _clean_plan(self, data):
        if type(data) == list:
            for i in range(len(data)):
                self._clean_plan(data[i])
        elif type(data) == dict:
            for k in data:
                self._clean_plan(data[k])
            if '_ndx2p' in data:
                del data['_ndx2p']
            if '' in data:
                del data['']


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--name', default="GPTPLANNER", type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())


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
        a = GPTPlannerAgent(name=args.name, session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = GPTPlannerAgent(name=args.name, input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = GPTPlannerAgent(name=args.name, properties=properties)
        a.start_session()

    # wait for session
    session.wait()