####### Parsers, Formats, Utils
import os
import argparse
import logging
import json
import pydash


###### Communication
import asyncio

###### Blue
from blue.service import Service
from blue.blueerror import BlueError

##### Agent specifc
from openai import OpenAI


class OpenAIService(Service):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "OPENAI"
        super().__init__(**kwargs)

    def default_handler(self, message, properties=None, websocket=None):
        data = pydash.objects.get(message, 'data', {})
        api = data['api']
        pydash.objects.unset(data, 'api')

        response = {}

        # API Client
        if 'OPENAI_BASE_URL' in os.environ:
            client = OpenAI(base_url=os.environ.get('OPENAI_BASE_URL'))
        else:
            client = OpenAI()

        if api == 'ChatCompletion':
            # response = client.chat.completions.create(**data, extra_headers={"x-indeed-redact-allow": "LOCATION,PERSON,PHONE"})
            response = client.chat.completions.create(**data)
        else:
            error = BlueError()
            error.add_log('Unknown API')
            return {"status": "client_error", "error": error.get_dict()}

        return {"status": "success", "data": response.model_dump()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="OPENAI")
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
    s = OpenAIService(name=args.name, prefix=prefix, properties=properties)

    # run
    asyncio.run(s.start_listening_socket())
