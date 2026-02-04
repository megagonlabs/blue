import traceback
import sys
import json
import time
import pydash
import inspect


def get_instantiating_class_name():
    """
    Returns the name of the class where this object is being initialized.

    This utility inspects the stack frames to determine if the function is being
    called within the context of a class instantiation (e.g., inside `__init__`).

    Returns:
        Optional[str]: The name of the instantiating class if found.
        Returns None if initialized in a module, standard function, or static method
        where no `self` or `cls` context is available.
    """
    frame = None
    try:
        frame = inspect.currentframe()
        if frame:
            caller_frame = frame.f_back
            if caller_frame:
                context_frame = caller_frame.f_back
                if context_frame:
                    code_obj = context_frame.f_code
                    arg_count = code_obj.co_argcount
                    var_names = code_obj.co_varnames
                    if arg_count > 0:
                        first_arg_name = var_names[0]
                        first_arg_value = context_frame.f_locals.get(first_arg_name)
                        if hasattr(first_arg_value, '__class__') and not isinstance(first_arg_value, type):
                            return type(first_arg_value).__name__
                        if isinstance(first_arg_value, type):
                            return first_arg_value.__name__
    except Exception:
        return None
    finally:
        del frame
    return None


class StackContextMixin:
    """
    Mixin class that provides stack inspection capabilities to identify callers.

    This mixin is primarily used to identify which class and method invoked
    a specific function, aiding in debugging and logging context.
    """

    def get_calling_class_name(self, stack_depth=2):
        """
        Identifies the class name of the method that called this function.

        It inspects the call stack at the specified depth to find the frame,
        extracts the `self` argument, and verifies if the method belongs to
        that class or is inherited.

        Parameters:
            stack_depth (int, optional): The depth in the stack to inspect.
                Defaults to 2 (the immediate caller of this method's caller).

        Returns:
            str: The name of the calling class, or an error/status message
            (e.g., "Unknown (Stack too shallow)", "Error detecting source").
        """
        try:
            stack = inspect.stack()
            if len(stack) <= stack_depth:
                return "Unknown (Stack too shallow)"
            caller_frame = stack[stack_depth].frame
            caller_code = caller_frame.f_code
            caller_self = caller_frame.f_locals.get('self', None)
            func_name = caller_code.co_name
            if caller_self is None:
                return "Unknown (No 'self' found)"
            for cls in inspect.getmro(type(caller_self)):
                if func_name in cls.__dict__:
                    class_method = cls.__dict__[func_name]
                    try:
                        underlying_func = inspect.unwrap(class_method)
                    except Exception:
                        underlying_func = class_method
                    if getattr(underlying_func, '__code__', None) == caller_code:
                        return cls.__name__
            return f"{type(caller_self).__name__} (inherited)"
        except Exception as e:
            return f"Error detecting source: {e}"
        finally:
            if 'caller_frame' in locals():
                del caller_frame


class BlueError(StackContextMixin, Exception):
    """
    A unified, serializable exception class for the Blue platform.

    `BlueError` is designed to wrap existing exceptions or create new ones with
    rich context, including:
    - **Intent**: How the system should react (e.g., 'fatal', 'retry').
    - **Context**: Arbitrary dictionary data attached to the error.
    - **Logs**: A timeline of messages added to the error as it bubbles up.
    - **Stack Trace**: A structured, serializable stack trace.

    It supports "chaining" by initializing a new `BlueError` from an existing one,
    preserving the original timestamp and history while allowing new logs to be added.

    Attributes:
        timestamp (int): Unix timestamp (in milliseconds) of creation.
        type (str): The type name of the original exception (e.g., 'ValueError').
        intent (str): The severity or intended reaction (e.g., 'fatal', 'warning').
        context (Dict): Key-value pairs of metadata associated with the error.
        log (List[Dict]): A chronological list of log entries describing the error's journey.
        stack_trace (List[Dict]): structured stack trace frames.
    """

    def __init__(self, exception=None, description=None, intent="fatal", context={}):
        """
        Initialize the BlueError.

        Paramters:
            exception (Optional[Union[Exception, BlueError]]): The original exception to wrap.
                If it is already a `BlueError`, this acts as a copy/update constructor.
            description (Optional[str]): A human-readable description or log message
                to add immediately upon creation.
            intent (str, optional): The severity level or handling intent. Defaults to "fatal".
            context (Dict, optional): Additional metadata to merge into the error context.
        """
        super().__init__()
        if isinstance(exception, BlueError):
            existing_error = exception
            self.timestamp = existing_error.timestamp
            self.type = existing_error.type
            self.intent = existing_error.intent
            self.context = existing_error.context.copy() if existing_error.context else {}
            self.log = existing_error.log[:]
            self.stack_trace = existing_error.stack_trace[:]
            if description is not None:
                self.add_log(description, caller=get_instantiating_class_name())
            if context:
                pydash.objects.merge(self.context, context)
            return
        self.timestamp = int(time.time() * 1000)
        if exception:
            ex_type = type(exception)
            module_name = ex_type.__module__
            class_name = ex_type.__name__
            if module_name == 'builtins':
                self.type = class_name
            else:
                self.type = f"{module_name}.{class_name}"
        else:
            self.type = "Unknown BlueError"
        self.intent = intent
        self.context = context.copy() if context else {}
        self.log = []
        if description is not None:
            self.add_log(description, caller=get_instantiating_class_name())
        elif exception is not None:
            self.add_log(str(exception), caller=get_instantiating_class_name())
        exc_type, exc_value, exc_traceback = sys.exc_info()
        structured_trace = []
        if exc_traceback:
            frames = traceback.extract_tb(exc_traceback)
            for frame in frames:
                file_name = frame.filename.split('/')[-1]
                if not file_name == 'errorloom.py':
                    structured_trace.append(
                        {
                            'file': frame.filename,
                            'line_number': frame.lineno,
                            'function': frame.name,
                            'source_code': frame.line,
                        }
                    )
        self.stack_trace = structured_trace

    def set_intent(self, intent):
        """
        Updates the intent of the error (e.g., changing from 'fatal' to 'retry').

        Parameters:
            intent (str): The new intent string.
        """
        self.intent = intent

    def set_context(self, key, value):
        """
        Adds or updates a value in the error's context dictionary.
        Supports nested keys via dot notation (e.g., 'user.id').

        Parameters:
            key (str): The context key.
            value (Any): The value to store.
        """
        pydash.objects.set_(self.context, key, value)

    def add_log(self, description, caller=None):
        """
        Appends a new log entry to the error's history.

        Parameters:
            description (str): The message to log.
            caller (str, optional): The name of the calling class/component.
                If None, attempts to auto-detect the caller from the stack.
        """
        caller_name = self.get_calling_class_name(stack_depth=2)
        self.log.append({"timestamp": int(time.time() * 1000), "description": description, "caller": caller_name if caller is None else caller})

    def __str__(self):
        """
        Returns the JSON string representation of the error.
        """
        return json.dumps(self.get_dict())

    def get_dict(self):
        """
        Converts the BlueError into a serializable dictionary.

        Returns:
            Dict: A dictionary containing timestamp, type, intent, log, and stack_trace.
        """
        return {"timestamp": self.timestamp, "type": self.type, "intent": self.intent, "log": self.log, "stack_trace": self.stack_trace}

    def from_json(self, json_string):
        """
        Hydrates this BlueError instance from a JSON string.

        Parameters:
            json_string (str): The JSON representation of a BlueError.
        """
        data = json.loads(json_string)
        self.timestamp = pydash.objects.get(data, 'timestamp', int(time.time() * 1000))
        self.type = pydash.objects.get(data, 'type', 'Unknown BlueError')
        self.intent = pydash.objects.get(data, 'intent', 'fatal')
        self.log = pydash.objects.get(data, 'log', [])
        self.stack_trace = pydash.objects.get(data, 'stack_trace', [])
