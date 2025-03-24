###### Parsers, Formats, Utils
import logging

###### Blue
from blue.agent import Agent

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


##########################
### Agent.UserAgent
#
class UserAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "USER"
        super().__init__(**kwargs)

    
    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # user is not instructable
        self.properties['instructable'] = False
