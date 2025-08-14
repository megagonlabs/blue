###### Parsers, Formats, Utils
import time
import argparse
import logging
import time
import re
import json

from blue.utils import json_utils, uuid_utils, log_utils


###############
### Constant
#
class Constant:
    def __init__(self, c):
        self.c = c

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        elif isinstance(other, str):
            return self.c == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.c)


###############
### StringConstant
#
class StringConstant(Constant):
    def __init__(self, c):
        super().__init__(c)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)


###############
### Separator
#
class Separator(StringConstant):
    def __init__(self, c):
        super().__init__(c)


###############
### ConstantEncoder
#
class ConstantEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Constant):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)


# Common Constants
Separator.ENTITY = "___"
Separator.AGENT = "___"
Separator.TOOL = "___"
Separator.ID = ":"


###############
### Entity
#
class Entity:
    def __init__(self, name=None, id=None, sid=None, cid=None, prefix=None, suffix=None):

        if cid:
            self.cid = cid
            # extract name, id, prefix
            self.name, self.id = uuid_utils.extract_name_id(cid)
            self.sid = uuid_utils.extract_sid(cid)

            self.prefix = uuid_utils.extract_prefix(cid)
            # always assume suffix=None
            self.suffix = None
        else:
            if sid:
                self.sid = sid
                # extract name, id
                self.name, self.id = uuid_utils.extract_name_id(sid)
            else:
                self.name = name
                if id:
                    self.id = id
                else:
                    self.id = uuid_utils.create_uuid()

                self.sid = uuid_utils.concat_ids(self.name, self.id)

            self.cid = self.sid

            self.prefix = prefix
            self.suffix = suffix

            if self.prefix:
                self.cid = uuid_utils.concat_ids(self.prefix, self.cid)
            if self.suffix:
                self.cid = uuid_utils.concat_ids(self.cid, self.suffix)
