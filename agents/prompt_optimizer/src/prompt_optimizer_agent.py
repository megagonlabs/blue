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
import copy

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent, AgentFactory
from session import Session
from message import Message, MessageType, ContentType, ControlCode


##### DSPy
import dspy
import dsp
from dspy.teleprompt import BootstrapFewShot, MIPRO


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

# Prompt program
class PromptSignature(dspy.Signature):
    input = dspy.InputField(desc="")
    output = dspy.OutputField(desc="")

class PromptProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prompt_signature = dspy.Predict(PromptSignature)
    
    def forward(self, input):
        return self.prompt_signature(input=input)



# Prompt metric
def exact_match(example, pred, trace=None, frac=1.0):
    assert(type(example.output) is str or type(example.output) is list)
    
    if type(example.output) is str:
        return dsp.answer_match(pred.output, [example.output], frac=frac)
    else: # type(example.answer) is list
        return dsp.answer_match(pred.output, example.output, frac=frac)

class PromptOptimizerAgent(Agent):
    
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "PROMPTOPTIMIZER"
        super().__init__(**kwargs)
        self.program = PromptProgram()

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        # dspy configure
        dspy.settings.configure(lm=dspy.OpenAI(model='gpt-4o-mini', 
                                               api_key=self.properties['OPENAI_API_KEY']), rm=None)
      

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['dspy.service'] = "ws://localhost:8001"
        self.properties['prompt_model'] = "gpt-4o-mini"
        self.properties['task_model'] = "task_model"
        self.properties['num_candidates'] = 5
        self.properties['temperature'] = 0.7
        self.properties['max_bootstrapped_demos'] = 4
        self.properties['max_labeled_demos'] = 4 
        self.properties['num_trials'] = 5

    
    def process_examples(self, examples):
        # Convert a list of input-output pairs into dspy.Example objects
        logging.info(examples)
        return [dspy.Example(input=ex[0], output=ex[1]).with_inputs("input") for ex in examples]
    
    def optimize(self, examples, properties=None):
        examples = self.process_examples(examples)
        # Configuration for the optimization process
        config = dict(max_bootstrapped_demos=4, max_labeled_demos=4, num_trials=5)
        eval_kwargs = dict(num_threads=16, display_progress=True, display_table=0)  # Evaluation settings

        # Create a teleprompter instance with specified models and metrics
        teleprompter = MIPRO(prompt_model=dspy.OpenAI(model=properties['prompt_model']), 
                             task_model=dspy.OpenAI(model=properties['task_model']), 
                             metric=exact_match,  # Use exact match as the metric
                             num_candidates=properties['num_candidates'], 
                             init_temperature=properties['temperature'], 
                             verbose=True)  # Enable verbose output

        # Compile the teleprompter with the program and examples
        optimized_program = teleprompter.compile(self.program, trainset=examples, eval_kwargs=eval_kwargs, requires_permission_to_run=False, **config)
        prompt =  {name: param.dump_state() for name, param in optimized_program.named_parameters()}
        logging.info(json.dumps(properties, indent=3))
        return prompt.signature_instructions

    def build_optimizer_form(self):
        # design form
        examples_ui = {
            "type": "Control",
            "scope": "#/properties/examples",
            "options": {
                "detail": {
                    "type": "VerticalLayout",
                    "elements": [
                        {"type": "Label", "label": "Examples"},
                        {
                            "type": "HorizontalLayout",
                            "elements": [
                                {
                                    "type": "Control",
                                    "scope": "#/properties/text",
                                },
                                {
                                    "type": "Control",
                                    "scope": "#/properties/annotation",
                                },
                            ],
                        },
                    ],
                }
            }
        }

        form_ui = {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Label",
                    "label": "Prompt Optimizer",
                    "props": {"style": {"fontWeight": "bold"}},
                },
                {
                    "type": "Label",
                    "label": f"Specify prompt optimization configuration below:",
                    "props": {
                        "muted": True,
                        "style": {"marginBottom": 15, "fontStyle": "italic"},
                    },
                },
                {
                    "type": "HorizontalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "label": "Prompt Model",
                            "scope": "#/properties/prompt_model"
                        },
                        {
                            "type": "Control",
                            "label": "Task Model",
                            "scope": "#/properties/task_model"
                        }
                    ]
                },
                 {
                    "type": "HorizontalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "label": "Temperature",
                            "scope": "#/properties/temperature"
                        },
                        {
                            "type": "Control",
                            "label": "Max. Labeled Examples",
                            "scope": "#/properties/max_labeled_demos"
                        },
                         {
                            "type": "Control",
                            "label": "Num. Trials",
                            "scope": "#/properties/num_trials"
                        }
                    ]
                },
                {
                    "type": "Label",
                    "label": f"Provide examples of input text and output annotations",
                    "props": {
                        "muted": True,
                        "style": {"marginBottom": 15, "fontStyle": "italic"},
                    },
                },
                { "type": "VerticalLayout", "elements": [examples_ui] },
                {
                    "type": "Button",
                    "label": "Optimize",
                    "props": {
                        "intent": "success",
                        "action": "DONE",
                        "large": True,
                    },
                },
            ]
        }

        form_schema = {
            "type": "object",
            "properties": {
                "examples": {
                    "type": "array",
                    "title": "Examples",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "annotation": {"type": "string"},
                        },
                    },
                },
                "prompt_model": {"type": "string", "enum": [
                    "gpt-4o-mini",
                    "gpt-4o",
                ]},
                "task_model": {"type": "string", "enum": [
                    "gpt-4o-mini",
                    "gpt-4o",
                ]},
                "temperature": {
                    "type": "number"
                },
                "max_labeled_demos": {
                    "type": "number"
                },
                "num_trials": {
                    "type": "number"
                }
            },
        }

        form = {
            "schema": form_schema,
            "data": {"examples": []},
            "uischema": form_ui,
        }
        return form

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if input == "DEFAULT":
            if message.isEOS():
                # compute stream data
                stream_data = ""
                if worker:
                    stream_data = " ".join(worker.get_data('stream_data'))

                optimizer_form = self.build_optimizer_form()
                if worker:
                    worker.write_control(
                        ControlCode.CREATE_FORM, optimizer_form, output="FORM"
                    )
            
            elif message.isBOS():
                # init stream to empty array
                if worker:
                    worker.set_data('stream_data',[])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                logging.info(data)
                
                if worker:
                    worker.append_data('stream_data', data)
        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    form_id = data["form_id"]
                    action = data["action"]

                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")

                    # when the user clicked DONE
                    if action == "DONE":
                        ### get form data
                        # examples
                        examples = worker.get_stream_data(
                            "examples.value", stream=form_data_stream
                        )
                        logging.info(examples)

                        # prompt/task models
                        prompt_model =  worker.get_stream_data(
                            "prompt_model.value", stream=form_data_stream
                        )
                        task_model =  worker.get_stream_data(
                            "task_model.value", stream=form_data_stream
                        )

                        # other optimization configuration
                        temperature =  worker.get_stream_data(
                            "temperature.value", stream=form_data_stream
                        )
                        max_labeled_demos = worker.get_stream_data(
                            "max_labeled_demos.value", stream=form_data_stream
                        )
                        num_trials = worker.get_stream_data(
                            "num_trials.value", stream=form_data_stream
                        )
                        
                        # override properties from user
                        properties = copy.deepcopy(self.properties)
                        properties['prompt_model'] = prompt_model
                        properties['task_model'] = task_model
                        properties['temperature'] = temperature
                        properties['max_labeled_demos'] = max_labeled_demos
                        properties['num_trials'] = num_trials

                        # close form
                        args = {"form_id": form_id}
                        worker.write_control(
                            ControlCode.CLOSE_FORM, args, output="FORM"
                        )

                        ### OPTIMIZE
                        return self.optimize(examples, properties=properties)

                    else:
                        # save form data
                        path = data["path"]
                        timestamp = worker.get_stream_data(
                            path + ".timestamp", stream=form_data_stream
                        )

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:
                            worker.set_stream_data(
                                path,
                                {
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=form_data_stream,
                            )
    
        return None
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="PROMPTOPTIMIZER", type=str)
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
        
        af = AgentFactory(_class=PromptOptimizerAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = PromptOptimizerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = PromptOptimizerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()



