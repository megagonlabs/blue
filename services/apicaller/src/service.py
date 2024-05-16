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

##### Communication 
import asyncio
import websockets

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
            logging.info(message)
            l = len(message)
            logging.info(l)
            await websocket.send(str(l))
        except websockets.ConnectionClosedOK:
            break

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    logging.info('starting....')
    asyncio.run(main())

