###### Parsers, Utils
import logging
import json
import pydash

from copy import deepcopy

###### Backend, Databases
from redis.commands.json.path import Path


###### Blue
from blue.connection import PooledConnectionFactory
from blue.constant import StringConstant, ConstantEncoder


###############
### MessageType
#
class MessageType(StringConstant):
    """
    Message types for stream messages:

    - DATA: Represents data messages in the stream.
    - CONTROL: Represents control messages in the stream.
    """

    def __init__(self, c):
        super().__init__(c)


# constants, message type
MessageType.DATA = MessageType("DATA")
MessageType.CONTROL = MessageType("CONTROL")


###############
### ContentType
#
class ContentType(StringConstant):
    """
    Content types for stream messages:

    - INT: Integer data type.
    - FLOAT: Floating-point data type.
    - STR: String data type.
    - JSON: JSON data type.
    """

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
class ControlCode(StringConstant):
    """
    Control codes for control messages in the stream:
    - BOS: Beginning of Stream.
    - EOS: End of Stream.
    - CREATE_SESSION: Create a new session.
    - JOIN_SESSION: Join an existing session.
    - ADD_AGENT: Add an agent to the session.
    - REMOVE_AGENT: Remove an agent from the session.
    - EXECUTE_AGENT: Execute an agent within the session.
    - ADD_STREAM: Add a new stream to the session.
    - CREATE_FORM: Create a new form for user interaction.
    - UPDATE_FORM: Update an existing form.
    - CLOSE_FORM: Close an existing form.
    - PROGRESS: Indicate progress of an operation.
    - CREATE_PIPELINE: Create a new pipeline. (NOT USED)
    - JOIN_PIPELINE: Join an existing pipeline. (NOT USED)
    - EXECUTE_OPERATOR: Execute an operator within the pipeline. (NOT USED)
    """

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
    """
    Stream message class representing data and control messages.
    """

    def __init__(self, label, contents, content_type):
        """
        Initialize a Message object.

        Parameters:
            label: MessageType indicating whether the message is DATA or CONTROL.
            contents: The actual content of the message. For DATA, it can be int, float, str, or dict. For CONTROL, it is a dict with 'code' and 'args'.
            content_type: ContentType indicating the type of content (INT, FLOAT, STR, JSON).
        """
        self.id = None
        self.stream = None

        self.label = label
        self.contents = contents
        self.content_type = content_type

    def __getitem__(self, x):
        return getattr(self, x)

    def getLabel(self):
        """
        Get the label of the message.

        Returns:
            MessageType of the message (DATA or CONTROL).
        """

        return self.label

    def setID(self, id):
        """
        Set the ID of the message.

        Parameters:
            id: ID to be set for the message.
        """
        self.id = id

    def getID(self):
        """
        Get the ID of the message.

        Returns:
            ID of the message.
        """
        return self.id

    def setStream(self, stream):
        """
        Set the stream of the message.

        Parameters:
            stream: Stream to be set for the message.
        """
        self.stream = stream

    def getStream(self):
        """
        Get the stream of the message.

        Returns:
            Stream of the message.
        """
        return self.stream

    def getData(self):
        """
        Get the data contents of the message.

        Returns:
            The data contents of the message if it is of type DATA, None otherwise.
        """
        if self.isData():
            return self.contents
        return None

    def getContents(self):
        """
        Get the contents of the message.

        Returns:
            The contents of the message.
        """
        return self.contents

    def getContentType(self):
        """
        Get the content type of the message.

        Returns:
            ContentType of the message.
        """
        return self.content_type

    def isData(self):
        """
        Check if the message is of type DATA.

        Returns:
            True if the message is DATA, False otherwise.
        """
        return self.label == MessageType.DATA

    def isControl(self):
        """
        Check if the message is of type CONTROL.

        Returns:
            True if the message is CONTROL, False otherwise.
        """
        return self.label == MessageType.CONTROL

    def isBOS(self):
        """
        Check if the message is the beginning of a stream.

        Returns:
            True if the message is the beginning of a stream, False otherwise.
        """
        return self.label == MessageType.CONTROL and self.getCode() == ControlCode.BOS

    def isEOS(self):
        """
        Check if the message is the end of a stream.

        Returns:
            True if the message is the end of a stream, False otherwise.
        """
        return self.label == MessageType.CONTROL and self.getCode() == ControlCode.EOS

    def getCode(self):
        """
        Get the code of the message.

        Returns:
            ControlCode of the message if it is of type CONTROL, None otherwise.
        """
        if self.isControl():
            return self.contents['code']
        return None

    def getArgs(self):
        """
        Get the arguments of the message.

        Returns:
            Arguments of the message if it is of type CONTROL, None otherwise.
        """
        if self.isControl():
            return self.contents['args']
        return None

    def getArg(self, arg):
        """
        Get a specific argument of the message.

        Parameters:
            arg: The name of the argument to retrieve.

        Returns:
            The value of the argument if it is of type CONTROL, None otherwise.
        """
        if self.isControl():
            args = self.getArgs()
            if arg in args:
                return args[arg]
        return None

    def setArg(self, arg, value):
        """
        Set a specific argument of the message.

        Parameters:
            arg: The name of the argument to set.
            value: The value to set for the argument.
        """
        if self.isControl():
            self.contents['args'][arg] = value

    # special for EXECUTE_AGENT
    def getAgent(self):
        """
        Get the agent of the message in the control message EXECUTE_AGENT.

        Returns:
            The agent of the message if it is of type CONTROL and the code is EXECUTE_AGENT, None otherwise.
        """
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if "agent" in args:
                    return args['agent']

        return None

    def getAgentContext(self):
        """
        Get the context of the message in the control message EXECUTE_AGENT.

        Returns:
            The context of the message if it is of type CONTROL and the code is EXECUTE_AGENT, None otherwise.
        """
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if "context" in args:
                    return args['context']
        return None

    def getAgentProperties(self):
        """
        Get the properties of the message in the control message EXECUTE_AGENT.

        Returns:
            The properties of the message if it is of type CONTROL and the code is EXECUTE_AGENT, None otherwise.
        """
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if "properties" in args:
                    return args['properties']
        return {}

    def getAgentProperty(self, property):
        """
        Get a specific property of the message in the control message EXECUTE_AGENT.

        Parameters:
            property: The name of the property to retrieve.

        Returns:
            The value of the property if it is of type CONTROL and the code is EXECUTE_AGENT, None otherwise.
        """
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                properties = self.getAgentProperties()
                if property in properties:
                    return properties[property]
        return None

    def getInputParams(self):
        """
        Get the input parameters of the message in the control message EXECUTE_AGENT.

        Returns:
            The input parameters of the message if it is of type CONTROL and the code is EXECUTE_AGENT, None otherwise.
        """
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                args = self.getArgs()
                if "inputs" in args:
                    return args['inputs']
        return {}

    def getInputParam(self, param):
        """
        Get a specific input parameter of the message in the control message EXECUTE_AGENT.

        Parameters:
            param: The name of the input parameter to retrieve.

        Returns:
            The value of the input parameter if it is of type CONTROL and the code is EXECUTE_AGENT, None otherwise.
        """
        if self.isControl():
            if self.getCode() == ControlCode.EXECUTE_AGENT:
                params = self.getInputParams()
                if param in params:
                    return params[param]
        return None

    def fromJSON(message_json):
        """
        Deserialize a JSON-encoded message.

        Parameters:
            message_json: The JSON-encoded message to deserialize.

        Returns:
            A Message object representing the deserialized message.
        """
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
        """
        Serialize the message to a JSON-encoded string.

        Returns:
            A JSON-encoded string representing the message.
        """
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
    """
    Stream class for managing data in Redis.
    """

    def __init__(self, cid, properties={}):
        """
        Initialize the Stream with a unique identifier and optional properties.
        """
        self.cid = cid
        self._initialize(properties=properties)

        self._start()

    def _initialize(self, properties=None):
        """
        Initialize the stream with default and provided properties.

        Parameters:
            properties: Optional dictionary of properties to override defaults.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        """
        Initialize the default properties for the stream.
        """
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        """
        Update the properties of the stream.

        Parameters:
            properties: Optional dictionary of properties to update.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ##  data
    def _get_data_namespace(self):
        """
        Get the data namespace for the stream.

        Returns:
            (str): The data namespace string.
        """
        return self.cid + ":DATA"

    def _init_data_namespace(self):
        """
        Initialize the data namespace for the stream.
        """
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_data_namespace(),
            "$",
            {},
            nx=True,
        )

    def set_data(self, key, value):
        """
        Set the data for a specific key in the stream.

        Parameters:
            key: The key to set.
            value: The value to set.
        """
        self.connection.json().set(
            self._get_data_namespace(),
            "$." + key,
            value,
        )

    def get_data(self, key):
        """
        Get the data for a specific key in the stream.

        Parameters:
            key: The key to get.

        Returns:
            The value associated with the key, or None if the key does not exist.
        """
        value = self.connection.json().get(
            self._get_data_namespace(),
            Path("$." + key),
        )
        return self.__get_json_value(value)

    def get_all_data(self):
        """
        Get all data for the stream.

        Returns:
            (dict): A dictionary containing all data in the stream.
        """
        value = self.connection.json().get(
            self._get_data_namespace(),
            Path("$"),
        )
        return self.__get_json_value(value)

    def append_data(self, key, value):
        """
        Append data to a specific key in the stream.

        Parameters:
            key: The key to append to.
            value: The value to append.
        """
        self.connection.json().arrappend(
            self._get_data_namespace(),
            "$." + key,
            value,
        )

    def get_data_len(self, key):
        """
        Get the length of the data array for a specific key in the stream.

        Parameters:
            key: The key to get the length for.
        Returns:
            (int): The length of the data array, or 0 if the key does not exist.
        """
        return self.connection.json().arrlen(
            self._get_data_namespace(),
            Path("$." + key),
        )

    ##  metadata
    def _get_metadata_namespace(self):
        """Get the metadata namespace for the stream.

        Returns:
            (str): The metadata namespace string.
        """
        return self.cid + ":METADATA"

    def _init_metadata_namespace(self):
        """Initialize the metadata namespace for the stream."""
        # create metadata namespace
        return self.connection.json().set(self._get_metadata_namespace(), "$", {"created_by": "", "id": "", "tags": {}, "consumers": {}, "producers": {}}, nx=True)

    def set_metadata(self, key, value, nx=False):
        """
        Set the metadata for a specific key in the stream.

        Parameters:
            key: The key to set.
            value: The value to set.
            nx (bool): If True, set the value only if it does not already exist.
        """
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def get_metadata(self, key=""):
        """
        Get the metadata for a specific key in the stream.

        Parameters:
            key: The key to get.
        Returns:
            The value associated with the key, or None if the key does not exist.
        """
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

    def _start(self):
        """Start the stream by establishing a database connection and initializing metadata and data namespaces."""
        self._start_connection()

        # initialize session metadata
        self._init_metadata_namespace()

        # initialize session data
        self._init_data_namespace()

    def _start_connection(self):
        """Establish a database connection using the provided properties."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()
