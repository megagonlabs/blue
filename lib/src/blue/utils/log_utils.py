###### Parsers, Formats, Utils
import logging
import inspect
import logging, json, re
from inspect import getframeinfo, stack


##########################
### CustomFilter
#
class CustomFilter(logging.Filter):
    call_stack = ''

    def filter(self, record):
        record.call_stack = self.call_stack
        return True


def extract_call_stack(s, depth=3):
    call_stack = ""
    d = 0
    for i in range(len(s)):
        frame_info = getframeinfo(s[i][0])
        filename = frame_info.filename.split("/")[-1]
        lineno = frame_info.lineno
        # skip log_utils
        if filename == "log_utils.py":
            continue
        else:
            if d > 0:
                call_stack += "\u2190"
            call_stack += filename + ":" + str(lineno)
            d += 1
            if d >= depth:
                break
    return call_stack


def caller_reader(f, depth=3):
    def wrapper(self, *args):
        s = stack()
        self.filter.call_stack = extract_call_stack(s, depth=depth)
        return f(self, *args)

    return wrapper


class CustomJsonFormatter(logging.Formatter):
    def __init__(self, data_config, output_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_config = data_config
        self.output_format = output_format

    def format(self, record):
        log_entry = {}
        log_entry['output_format'] = self.output_format
        for item in self.data_config:
            field_name = item['name']
            format_spec = item['format']
            if field_name == 'time' and '%(asctime)s' in format_spec:
                log_entry[field_name] = self.formatTime(record, self.datefmt)
            elif field_name == 'message' and '%(message)s' in format_spec:
                log_entry[field_name] = record.getMessage()
            else:
                match = re.match(r'%\((.*?)\)s', format_spec)
                attr_name = match.group(1) if match else field_name
                value = getattr(record, attr_name, None)
                if value is not None:
                    log_entry[field_name] = value
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        if record.stack_info:
            log_entry['stack_trace'] = self.formatStack(record.stack_info)
        return json.dumps(log_entry)


##########################
### CustomLogger
#
class CustomLogger:
    def __init__(self, config=None):
        self.root_logger = logging.getLogger()
        if config is None:
            self._init_default_config()
        else:
            self.config = config
        self.filter = CustomFilter()
        self._initialized = False
        # self._initialize()

    def _init_default_config(self):
        self.config = {}
        self.config['options'] = {"datefmt": "%Y-%m-%d %H:%M:%S"}
        self.config['output'] = {"format": "json"}
        self.config['data'] = [
            {"name": "time", "format": "%(asctime)s"},
            {"name": "level", "format": "%(levelname)s"},
            {"name": "process", "format": "%(process)d:%(threadName)s:%(thread)d"},
            {"name": "stack", "format": "%(filename)s:%(lineno)d"},
            {"name": "message", "format": "%(message)s"},
        ]

    def set_config_option(self, key, value):
        self.config['options'][key] = value
        self._initialized = False

    def del_config_option(self, key):
        del self.config['options'][key]
        self._initialized = False

    def set_config_output(self, key, value):
        self.config['output'][key] = value
        self._initialized = False

    def del_config_output(self, key):
        del self.config['output'][key]
        self._initialized = False

    def set_config_data(self, key, format, index=None):
        exists = False
        existing_index = -1
        existing_config = None
        for i, c in enumerate(self.config['data']):
            if c['name'] == key:
                exists = True
                existing_index = i
                existing_config = c
                break

        if index is None:
            if exists:
                # replace in place
                existing_config['format'] = format
            else:
                index = len(self.config['data'])
                self.config['data'].insert(index, {"name": key, "format": format})
        else:
            if exists:
                # delete first
                del self.config['data'][existing_index]
            self.config['data'].insert(index, {"name": key, "format": format})

        self._initialized = False

    def del_config_data(self, key):
        # identify index
        index = None
        for i, d in enumerate(self.config['data']):
            if d['name'] == key:
                index = i
        # del
        if index:
            del self.config['data'][index]
        self._initialized = False

    def setLevel(self, log_level):
        self.logger.setLevel(log_level)

    def debug(self, message, *args, **kwargs):
        self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self.log(logging.INFO, message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        self.log(logging.WARN, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.log(logging.ERROR, message, *args, **kwargs)

    def fatal(self, message, *args, **kwargs):
        self.log(logging.FATAL, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.log(logging.CRITICAL, message, *args, **kwargs)

    @caller_reader
    def log(self, level, message, *args, **kwargs):
        if not self._initialized:
            self._initialize()
        self.logger.log(level, message, *args, **kwargs)

    def _initialize(self):
        if self.root_logger.hasHandlers():
            self.root_logger.handlers.clear()
        self.handler = logging.StreamHandler()
        if self.config['output']['format'] == "json":
            formatter = CustomJsonFormatter(self.config['data'], self.config['output']['format'], **self.config['options'])
        else:
            formatter_str_parts = []
            for d in self.config['data']:
                formatter_str_parts.append(f"[{d['name']}={d['format']}]")
            formatter = logging.Formatter(" ".join(formatter_str_parts), **self.config['options'])

        self.handler.setFormatter(formatter)
        self.handler.addFilter(self.filter)
        self.root_logger.addHandler(self.handler)
        self.logger = logging.LoggerAdapter(self.root_logger, {})


# cl = CustomLogger()

# cl.set_config_data("session", "SESSION:123", -1)

# cl.info("hello")
# cl.warn("this is a warning")
