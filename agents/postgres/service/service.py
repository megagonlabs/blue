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
import psycopg2

# set log level
logging.getLogger().setLevel(logging.INFO)

async def handler(websocket):
    while True:
        try:
            s = await websocket.recv()
            logging.info(s)
            print(s)

            message = json.loads(s)
            
            query = message['query']
            del message['query']

            # Connect to database
            connection = psycopg2.connect(**message)

            # Get cursor, execute query, fetch all data
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            # get results
            results = list(data)

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
