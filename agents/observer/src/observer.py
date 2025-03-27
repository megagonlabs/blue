###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.agent import Agent, AgentFactory
from blue.agents.observer import ObserverAgent
from blue.session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="OBSERVER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str)
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

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

        af = AgentFactory(
            _class=ObserverAgent,
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
            a = ObserverAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = ObserverAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
