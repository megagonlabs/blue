###### Parsers, Formats, Utils
import logging

###### Blue
from blue.agent import Agent
from blue.session import Session


# set log level
logging.getLogger().setLevel(logging.INFO)

# create a session
session = Session()

prefix = session.cid + ":" + "AGENT"

# create a user agent
user_agent = Agent(name="USER", prefix=prefix, session=session)

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
        # store data value
        data = message.getData()
        print(data)
        stream_data.append(data)
        return None
    
# create a counter agent in the same session
properties = {
    "listens": {
        "DEFAULT": {
          "includes": [
            "USER"
          ],
          "excludes": []
        }
      }
}
counter_agent = Agent(name="COUNTER", prefix=prefix, properties=properties, session=session, processor=processor)