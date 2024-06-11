import sys

sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')

from agent import Agent, AgentFactory
from session import Session

# create a session
session = Session()

# create a user agent
user_agent = Agent(name="USER", session=session)

# user initiates an interaction
user_agent.interact("hello world!")

# sample func to process data for counter
stream_data = []

def processor(stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
    if label == 'EOS':
        # print all data received from stream
        print(stream_data)
        # compute stream data
        l = len(stream_data)
        # output to stream
        return l 
    elif label == 'DATA':
        # store data value
        stream_data.append(data)
        return None

# create a counter agent in the same session
counter_agent = Agent("COUNTER", session=session, processor=processor)

# wait for session
if session:
    session.wait()

