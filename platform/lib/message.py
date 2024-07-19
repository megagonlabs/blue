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
class Message():
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
        
    def toJSON(self):
        d = deepcopy(self.__dict__)
        # remove id, stream
        del d["id"]
        del d["stream"]
        # convert to JSON
        return self._toJSON(d)
    
    def _toJSON(self, v):
        if type(v) == dict:
            for k in v:
                v[k] = self._toJSON(v[k])
            return(v)
        elif type(v) == MessageType or type(v) == ContentType or type(v) == ControlCode:
            return str(v)
        else:
            return v

    def __str__(self):
        return json.dumps(self.toJSON(), cls=MessageEncoder)
    
# constants
Message.BOS=Message(MessageType.CONTROL, {"code": ControlCode.BOS, "args": {}}, ContentType.JSON)
Message.EOS=Message(MessageType.CONTROL, {"code": ControlCode.EOS, "args": {}}, ContentType.JSON)

class MessageEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            return obj.toJSON()
        
        return super().default(obj)

class MessageDecoder(JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(object_hook=MessageDecoder.from_dict, **kwargs)

    @staticmethod
    def from_dict(d):
        if 'label' in d and 'contents' in d and 'type' in d:
            d['label'] = MessageType(d['label'])
            d['type'] = ContentType(d['type'])
        if 'code' in d and 'args' in d:
            d['code'] = ControlCode(d['code'])
        return d