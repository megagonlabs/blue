import sys

sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')

from agent import Agent
from session import Session

import logging

# set log level
logging.getLogger().setLevel(logging.INFO)

# create a session
session = Session()

# create a user agent
user_agent = Agent(name="USER", session=session)

# user initiates an interaction
user_agent.interact("hello world!", eos=False)
user_agent.interact("i am an agent")

# sample func to process data for counter
stream_data = []

def processor(message, input=None, properties=None, worker=None):
    if message.isEOS():
        # print all data received from stream
        print("Stream Data:")
        print(stream_data)
        # compute length of the stream data
        l = len(stream_data)
        print(l)
        # output to stream
        return l 
    elif message.isData():
        print(input)
        print(properties)
        print(message)
        print(message.getID())
        print(message.getStream())
        # store data value
        data = message.getData()
        print(data)
        stream_data.append(data)
        return None

# create a counter agent in the same session
counter_agent = Agent(name="COUNTER", session=session, processor=processor)

# wait for session
if session:
    session.wait()

