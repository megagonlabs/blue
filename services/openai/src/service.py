###### OS / Systems
import os
import sys

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

##### Communication 
import asyncio
import websockets

##### Agent specifc
from openai import OpenAI

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


async def handler(websocket):
    while True:
        try:
            s = await websocket.recv()
            logging.info(s)
            print(s)

            message = json.loads(s)
            api = message['api']
            del message['api']

            if 'OPENAI_BASE_URL' in os.environ:
                client = OpenAI(base_url=os.environ.get('OPENAI_BASE_URL'))
            else:
                client = OpenAI()
            if api == 'ChatCompletion':
                response = client.chat.completions.create(**message)
            else:
                raise Exception('unknown api') 
            

            logging.info(response.json())
            await websocket.send(response.json())

        except websockets.ConnectionClosedOK:
            break

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    logging.info('starting....')
    asyncio.run(main())
