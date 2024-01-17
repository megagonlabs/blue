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
import openai

# set log level
logging.getLogger().setLevel(logging.INFO)

async def handler(websocket):
    while True:
        try:
            s = await websocket.recv()
            logging.info(s)
            print(s)

            message = json.loads(s)
            api = message['api']
            del message['api']

            if api == 'Completion':
                response = openai.Completion.create(**message)
            elif api == 'ChatCompletion':
                response = openai.ChatCompletion.create(**message)
            elif api == 'Edit':
                response = openai.Edit.create(**message)
            else:
                raise Exception('unknown api') 
            

            logging.info(json.dumps(response))
            await websocket.send(json.dumps(response))

        except websockets.ConnectionClosedOK:
            break

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    logging.info('starting....')
    asyncio.run(main())
