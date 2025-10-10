###### Parsers, Formats, Utils
import logging
import inspect
import logging, json, re
from inspect import getframeinfo, stack
from blue.utils import string_utils


##########################
### CustomFilter
#
class CustomFilter(logging.Filter):
    """Custom filter which adds the call stack to the log record."""

    call_stack = ''

    def filter(self, record):
        record.call_stack = self.call_stack
        return True


def extract_call_stack(s, depth=8):
    call_stack = []
    for i in range(len(s)):
        if len(call_stack) >= depth:
            break
        frame_info = getframeinfo(s[i][0])
        filename = frame_info.filename.split("/")[-1]
        lineno = frame_info.lineno
        # skip log_utils
        if filename == "log_utils.py":
            continue
        else:
            call_stack.append(filename + ":" + str(lineno))

    return ";".join(call_stack)


def caller_reader(f, depth=3):
    def wrapper(self, *args):
        s = stack()
        self.filter.call_stack = extract_call_stack(s, depth=depth)
        return f(self, *args)

    return wrapper


def replace_template(match):
    key = str(match.group(1))
    return "${" + key + "}"


class CustomJsonFormatter(logging.Formatter):
    """Custom JSON formatter for log records."""

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
                template = re.sub(r"%\((.*?)\).?", replace_template, format_spec)
                value = string_utils.safe_substitute(template, **record.__dict__)
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
    """Custom logger with configurable format and output."""

    def __init__(self, config=None):
        """Initialize the CustomLogger.

        Parameters:
            config: Configuration dictionary for the logger. If None, default configuration is used.

        """
        self.root_logger = logging.getLogger()
        if config is None:
            self._init_default_config()
        else:
            self.config = config
        self.filter = CustomFilter()
        self._initialized = False
        # self._initialize()

    def _init_default_config(self):
        """Initialize the default configuration for the logger."""
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
        """Set a configuration option for the logger.

        Parameters:
            key: Key of the configuration option.
            value: Value of the configuration option.
        """
        self.config['options'][key] = value
        self._initialized = False

    def del_config_option(self, key):
        """Delete a configuration option for the logger.

        Parameters:
            key: Key of the configuration option to delete.
        """
        del self.config['options'][key]
        self._initialized = False

    def set_config_output(self, key, value):
        """Set a configuration output option for the logger.

        Parameters:
            key: Key of the configuration output option.
            value: Value of the configuration output option.
        """
        self.config['output'][key] = value
        self._initialized = False

    def del_config_output(self, key):
        del self.config['output'][key]
        self._initialized = False

    def set_config_data(self, key, format, index=None):
        """Set a configuration data option for the logger.

        Parameters:
            key: Key of the configuration data option.
            format: Format string for the configuration data option.
            index: Optional index to insert the configuration data option at. If None, append to the end.
        """
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
        """Delete a configuration data option for the logger.

        Parameters:
            key: Key of the configuration data option to delete.
        """
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
        """Set the logging level for the logger.

        Parameters:
            log_level: Logging level to set (e.g., logging.DEBUG, logging.INFO).
        """
        self.logger.setLevel(log_level)

    def debug(self, message, *args, **kwargs):
        """Log a message with DEBUG level.

        Parameters:
            message: Message to log.
        """
        self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """Log a message with INFO level.

        Parameters:
            message: Message to log.
        """
        self.log(logging.INFO, message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        """Log a message with WARN level.

        Parameters:
            message: Message to log.
        """
        self.log(logging.WARN, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Log a message with ERROR level.

        Parameters:
            message: Message to log.
        """
        self.log(logging.ERROR, message, *args, **kwargs)

    def fatal(self, message, *args, **kwargs):
        """Log a message with FATAL level.

        Parameters:
            message: Message to log.
        """
        self.log(logging.FATAL, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """Log a message with CRITICAL level.

        Parameters:
            message: Message to log.
        """
        self.log(logging.CRITICAL, message, *args, **kwargs)

    @caller_reader
    def log(self, level, message, *args, **kwargs):
        """Log a message with the specified level.

        Parameters:
            level: Logging level (e.g., logging.DEBUG, logging.INFO).
            message: M
        """
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
