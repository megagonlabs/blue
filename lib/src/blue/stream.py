###### Parsers, Utils
import logging
import json
import pydash

from copy import deepcopy

###### Backend, Databases
from redis.commands.json.path import Path


###### Blue
from blue.connection import PooledConnectionFactory

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


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
        return self.c

###############
### ConstantEncoder
#
class ConstantEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Constant):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)

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
ControlCode.CREATE_SESSION = ControlCode("CREATE_SESSION")
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
# progress
ControlCode.PROGRESS = ControlCode('PROGRESS')
# operators
ControlCode.CREATE_PIPELINE = ControlCode("CREATE_PIPELINE")
ControlCode.JOIN_PIPELINE = ControlCode("JOIN_PIPELINE")
ControlCode.EXECUTE_OPERATOR = ControlCode("EXECUTE_OPERATOR")


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
        return None

    def getArgs(self):
        if self.isControl():
            return self.contents['args']
        return None

    def getArg(self, arg):
        if self.isControl():
            args = self.getArgs()
            if arg in args:
                return args[arg]
        return None

    def setArg(self, arg, value):
        if self.isControl():
            self.contents['args'][arg] = value


    # special for EXECUTE_AGENT
    def getAgent(self):
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if "agent" in args:
                    return args['agent']
                
        return None

    def getAgentContext(self):
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if  "context" in args:
                    return args['context']
        return None

    def getAgentProperties(self):
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if  "properties" in args:
                    return args['properties']
        return {}
    
    def getAgentProperty(self, property):
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                properties = self.getAgentProperties()
                if property in properties:
                    return properties[property]
        return None
     
    def getInputParams(self):
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if  "inputs" in args:
                    return args['inputs']
        return {}
    
    def getInputParam(self, param):
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                params = self.getInputParams()
                if param in params:
                    return params[param]
        return None




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
            d['contents'] = json.dumps(contents, cls=ConstantEncoder)
        else:
            if self.content_type == ContentType.JSON:
                d['contents'] = json.dumps(self.contents, cls=ConstantEncoder)
            else:
                d['contents'] = self.contents

        # convert to JSON
        return json.dumps(d, cls=ConstantEncoder)

    def __str__(self):
        return self.toJSON()


# constants
Message.BOS = Message(MessageType.CONTROL, {"code": ControlCode.BOS, "args": {}}, ContentType.JSON)
Message.EOS = Message(MessageType.CONTROL, {"code": ControlCode.EOS, "args": {}}, ContentType.JSON)


###############
### Stream
#
class Stream:
    def __init__(self, cid, properties={}):
        self.cid = cid
        self._initialize(properties=properties)
        self._start_connection()

    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    def __get_json_value(self, value):
        if value is None:
            return None
        if type(value) is list:
            if len(value) == 0:
                return None
            else:
                return value[0]
        else:
            return value



