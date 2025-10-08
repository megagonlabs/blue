###### Parsers, Formats, Utils
import json


###############
### Constant
#
class Constant:
    """Base class for constants."""

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
    """Class for string constants."""

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
    """Class for separator constants."""

    def __init__(self, c):
        super().__init__(c)


###############
### ConstantEncoder
#
class ConstantEncoder(json.JSONEncoder):
    """Custom JSON encoder for Constant objects."""

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
