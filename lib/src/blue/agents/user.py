###### Parsers, Formats, Utils
import logging

###### Blue
from blue.agent import Agent


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
