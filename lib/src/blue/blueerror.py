import traceback
import sys
import json
import time
import pydash


class BlueError(Exception):
    def __init__(self, exception=None, description=None, intent="fatal", context={}):
        super().__init__()
        if isinstance(exception, BlueError):
            existing_error = exception
            self.timestamp = existing_error.timestamp
            self.type = existing_error.type
            self.intent = existing_error.intent
            self.context = existing_error.context.copy() if existing_error.context else {}
            self.description = existing_error.description[:]
            self.stack_trace = existing_error.stack_trace[:]
            if description is not None:
                self.add_description(description)
            if context:
                pydash.objects.merge(self.context, context)
            return
        self.timestamp = int(time.time() * 1000)
        self.type = type(exception).__name__ if exception is not None else "UnknownError"
        self.intent = intent
        self.context = context.copy() if context else {}
        self.description = []
        if description is not None:
            self.description.append({"timestamp": self.timestamp, "description": description})
        elif exception is not None:
            self.description.append({"timestamp": self.timestamp, "description": str(exception)})
        exc_type, exc_value, exc_traceback = sys.exc_info()
        structured_trace = []
        if exc_traceback:
            frames = traceback.extract_tb(exc_traceback)
            for frame in frames:
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
        self.intent = intent

    def set_context(self, key, value):
        pydash.objects.set_(self.context, key, value)

    def add_description(self, description):
        self.description.append({"timestamp": int(time.time() * 1000), "description": description})

    def __str__(self):
        return json.dumps(self.get_dict())

    def get_dict(self):
        return {"timestamp": self.timestamp, "type": self.type, "intent": self.intent, "description": self.description, "stack_trace": self.stack_trace}

    def from_json(self, json_string):
        data = json.loads(json_string)
        self.timestamp = pydash.objects.get(data, 'timestamp', int(time.time() * 1000))
        self.type = pydash.objects.get(data, 'type', 'UnknownError')
        self.intent = pydash.objects.get(data, 'intent', 'fatal')
        self.description = pydash.objects.get(data, 'description', [])
        self.stack_trace = pydash.objects.get(data, 'stack_trace', [])
