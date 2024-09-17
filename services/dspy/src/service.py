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
import json

##### Communication 
import asyncio
import websockets

###### dspy
import dspy

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

#######################    
class ExtractOperator(dspy.Signature):
    """Given a natural language text, tag the named entities with [MEN] and [/MEN]"""

    text = dspy.InputField(desc="natural language text without entity annotations")
    annotated_text = dspy.OutputField(desc="natural language text with annotations", prefix='')

### dspy extact operator
dspy_operator = dspy.Predict(ExtractOperator)
llm = dspy.OpenAI(model='gpt-4o')

### dspy configuration
dspy.settings.configure(lm=llm, rm=None)


async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
            logging.info(message)

            # process message
            message = json.loads(message)
            budget = message['budget']
            input = message['input']

            # prepare output, return
            output = dspy_operator(text=input)

            result = {}
            result['output'] = output.annotated_text

            await websocket.send(json.dumps(output))
        except websockets.ConnectionClosedOK:
            break

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    logging.info('starting....')
    asyncio.run(main())

