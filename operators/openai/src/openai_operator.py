###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.operator import OperatorFactory
from blue.operator.openai import OpenAIOperator

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="OPENAI")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str, default="OPERATOR")
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

        of = OperatorFactory(
            _class=OpenAIOperator,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        of.wait()