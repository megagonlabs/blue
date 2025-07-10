####### Parsers, Formats, Utils
import argparse
import logging
import json


###### Communication
import asyncio

###### Blue
from blue.service import Service


class RequestorService(Service):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "REQUESTOR"
        super().__init__(**kwargs)

    def default_handler(self, message, properties=None, websocket=None):
        self.logger.info(message)
        l = len(message)
        self.logger.info(l)

        return {"length": l}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="REQUESTOR")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--platform", type=str, default="default")

    args = parser.parse_args()

    # logging
    logging.getLogger().setLevel(logging.getLevelName(args.loglevel.upper()))

    # set properties
    properties = {}
    p = args.properties

    print(args)
    if p:
        # decode json
        properties = json.loads(p)

    # create service
    prefix = "PLATFORM:" + args.platform + ":SERVICE"
    s = RequestorService(name=args.name, prefix=prefix, properties=properties)

    # run
    asyncio.run(s.start_listening_socket())
