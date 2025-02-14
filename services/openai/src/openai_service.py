####### Parsers, Formats, Utils
import os
import argparse
import logging
import json


###### Communication
import asyncio

###### Blue
from blue.service import Service

##### Agent specifc
from openai import OpenAI

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

class OpenAIService(Service):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "OPENAI"
        super().__init__(**kwargs)


    def default_handler(self, message, properties=None, websocket=None):
        api = message['api']
        del message['api']

        response = {}

        # API Client
        if 'OPENAI_BASE_URL' in os.environ:
            client = OpenAI(base_url=os.environ.get('OPENAI_BASE_URL'))
        else:
            client = OpenAI()


        if api == 'ChatCompletion':
            # response = client.chat.completions.create(**message, extra_headers={"x-indeed-redact-allow": "LOCATION,PERSON,PHONE"})
            response = client.chat.completions.create(**message)
        else:
            response['error'] = "Unknown API"
        
        return response


if __name__ == "__main__":
    logging.info('starting....')
 

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="OPENAI")
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
    s = OpenAIService(name=args.name, prefix=prefix, properties=properties)

    # run
    asyncio.run(s.start_listening_socket())
    