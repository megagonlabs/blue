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
from neo4j_connection import NEO4J_Connection

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
            
            query = message['query']

            # Connect to database 
            host = message['host']
            user = message['user']
            pwd = message['password']
            connection = NEO4J_Connection(host, user, pwd)

            # Execute query, fetch all data
            data = connection.run_query(query)

            # get results
            results = data

            logging.info(results)
            
            response = {}
            response['results'] = results

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
