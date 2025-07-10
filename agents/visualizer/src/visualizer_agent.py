###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.agent import Agent, AgentFactory
from blue.agents.visualizer import VisualizerAgent
from blue.session import Session


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="VISUALIZER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str)
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

    args = parser.parse_args()

    # logging
    logging.getLogger().setLevel(logging.getLevelName(args.loglevel.upper()))

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.serve:
        platform = args.platform

        af = AgentFactory(
            _class=VisualizerAgent,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = VisualizerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = VisualizerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
