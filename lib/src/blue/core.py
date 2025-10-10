###### Parsers, Formats, Utils
import time
import argparse
import logging
import time
import re
import json

from blue.utils import json_utils, uuid_utils, log_utils


###############
### Entity
#
class Entity:
    """Base class for entities with unique identifiers for common entities in blue."""

    def __init__(self, name=None, id=None, sid=None, cid=None, prefix=None, suffix=None):
        """Initialize the Entity.

        Parameters:
            name: Name of the entity.
            id: Unique identifier for the entity.
            sid: Short identifier (combination of name and id).
            cid: Canonical identifier (may include prefix and suffix).
            prefix: Optional prefix for the cid.
            suffix: Optional suffix for the cid.
        """
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
