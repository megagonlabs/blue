###### Parsers, Formats, Utils
import argparse
import logging
import json
import threading

###### Blue
from blue.agent import Agent, AgentFactory
from blue.agents.blocking_agent import BlockingAgent
from blue.agents.openai import OpenAIAgent
from blue.stream import Message
from blue.session import Session


############################
### Agent.BlockingOpenAIAgent
#
class BlockingOpenAIAgent(BlockingAgent, OpenAIAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def process_logic(self, input_dict, worker):
        return super().execute_api_call(input=str(input_dict), properties=self.properties)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="BLOCKING_OPENAI", type=str)
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

        af = AgentFactory(_class=BlockingOpenAIAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = BlockingOpenAIAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = BlockingOpenAIAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
