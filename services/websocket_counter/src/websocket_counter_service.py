####### Parsers, Formats, Utils
import argparse
import logging
import json


###### Communication
import asyncio

###### Blue
from blue.service import Service

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

class WebSocketCounterService(Service):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "WEBSOCKET_COUNTER"
        super().__init__(**kwargs)


    def default_handler(self, message, properties=None, websocket=None):
        logging.info(message)
        l = len(message)
        logging.info(l)
        
        return { "length": l}
    
if __name__ == "__main__":
    logging.info('starting....')
 

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="WEBSOCKET_COUNTER")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--platform", type=str, default="default")

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties

    print(args)
    if p:
        # decode json
        properties = json.loads(p)
        print("properties:")
        print(json.dumps(properties, indent=3))
        print("---")

    # create service
    prefix = "PLATFORM:" + args.platform + ":SERVICE"
    s = WebSocketCounterService(name=args.name, prefix=prefix, properties=properties)

    # run
    asyncio.run(s.start_listening_socket())
    
