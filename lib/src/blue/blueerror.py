import traceback
import sys
import json
import time


class BlueError(Exception):
    def __init__(self, exception, description=None, intent="fatal"):
        super().__init__()
        self.timestamp = int(time.time() * 1000)
        self.type = type(exception).__name__
        self.intent = intent
        self.description = [{"timestamp": self.timestamp, "description": str(exception) if description is None else description}]
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

    def add_description(self, description):
        self.description.append({"timestamp": int(time.time() * 1000), "description": description})

    def __str__(self):
        return json.dumps({"timestamp": self.timestamp, "type": self.type, "intent": self.intent, "description": self.description, "stack_trace": self.stack_trace}, indent=4)

    def get_dict(self):
        return {"timestamp": self.timestamp, "type": self.type, "intent": self.intent, "description": self.description, "stack_trace": self.stack_trace}
