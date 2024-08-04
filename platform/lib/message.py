from json import JSONEncoder, JSONDecoder
import json

from copy import deepcopy


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
        return self.c


###############
### MessageType
#
class MessageType(Constant):
    def __init__(self, c):
        super().__init__(c)


# constants, message type
MessageType.DATA = MessageType("DATA")
MessageType.CONTROL = MessageType("CONTROL")


###############
### ContentType
#
class ContentType(Constant):
    def __init__(self, c):
        super().__init__(c)


# constants, content type
ContentType.INT = ContentType("INT")
ContentType.FLOAT = ContentType("FLOAT")
ContentType.STR = ContentType("STR")
ContentType.JSON = ContentType("JSON")


###############
### ControlCode
#
class ControlCode(Constant):
    def __init__(self, c):
        super().__init__(c)


# constants, control codes
# stream codes
ControlCode.BOS = ControlCode("BOS")
ControlCode.EOS = ControlCode("EOS")
# platform codes
ControlCode.JOIN_SESSION = ControlCode("JOIN_SESSION")
# session codes
ControlCode.ADD_AGENT = ControlCode("ADD_AGENT")
ControlCode.REMOVE_AGENT = ControlCode("REMOVE_AGENT")
ControlCode.EXECUTE_AGENT = ControlCode("EXECUTE_AGENT")
ControlCode.ADD_STREAM = ControlCode("ADD_STREAM")
# interaction codes
ControlCode.CREATE_FORM = ControlCode("CREATE_FORM")
ControlCode.UPDATE_FORM = ControlCode("UPDATE_FORM")
ControlCode.CLOSE_FORM = ControlCode("CLOSE_FORM")


###############
### Message
#
class Message:
    def __init__(self, label, contents, content_type):
        self.id = None
        self.stream = None

        self.label = label
        self.contents = contents
        self.content_type = content_type

    def __getitem__(self, x):
        return getattr(self, x)

    def getLabel(self):
        return self.label

    def setID(self, id):
        self.id = id

    def getID(self):
        return self.id

    def setStream(self, stream):
        self.stream = stream

    def getStream(self):
        return self.stream

    def isData(self):
        return self.label == MessageType.DATA

    def getData(self):
        if self.isData():
            return self.contents
        else:
            return None

    def getContents(self):
        return self.contents

    def getContentType(self):
        return self.content_type

    def isData(self):
        return self.label == MessageType.DATA

    def isControl(self):
        return self.label == MessageType.CONTROL

    def isBOS(self):
        return self.label == MessageType.CONTROL and self.getCode() == ControlCode.BOS

    def isEOS(self):
        return self.label == MessageType.CONTROL and self.getCode() == ControlCode.EOS

    def getCode(self):
        if self.isControl():
            return self.contents['code']
        else:
            return None

    def getArgs(self):
        if self.isControl():
            return self.contents['args']
        else:
            return None

    def getParam(self, param):
        if self.isData():
            if param in self.contents['params']:
                return self.contents['params'][param]
            else:
                return None
        else:
            return None

    def getParams(self):
        if self.isData():
            return self.contents['args']['params']
        else:
            return None

    def getArg(self, arg):
        if self.isControl():
            if arg in self.contents['args']:
                return self.contents['args'][arg]
            else:
                return None
        else:
            return None

    def setArg(self, arg, value):
        if self.isControl():
            self.contents['args'][arg] = value

    def fromJSON(message_json):
        d = json.loads(message_json)
        label = MessageType(d['label'])
        content_type = ContentType(d['content_type'])
        contents = d['contents']
        if content_type == ContentType.JSON:
            contents = json.loads(contents)
            if label == MessageType.CONTROL:
                contents['code'] = ControlCode(contents['code'])
        return Message(label, contents, content_type)

    def toJSON(self):
        d = deepcopy(self.__dict__)
        # remove id, stream
        del d['id']
        del d['stream']
        # convert types to str, when necessary
        d['label'] = str(self.label)
        d['content_type'] = str(self.content_type)
        if self.label == MessageType.CONTROL:
            contents = d['contents']
            contents['code'] = str(contents['code'])
            d['contents'] = json.dumps(contents)
        else:
            if self.content_type == ContentType.JSON:
                d['contents'] = json.dumps(self.contents)
            else:
                d['contents'] = self.contents

        # convert to JSON
        return json.dumps(d)

    def __str__(self):
        return self.toJSON()


# constants
Message.BOS = Message(MessageType.CONTROL, {"code": ControlCode.BOS, "args": {}}, ContentType.JSON)
Message.EOS = Message(MessageType.CONTROL, {"code": ControlCode.EOS, "args": {}}, ContentType.JSON)
