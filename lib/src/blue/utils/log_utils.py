###### Parsers, Formats, Utils
import logging


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
        self._initialized = False
        self._initialize()

    def _init_default_config(self):
        self.config = {}
        self.config['options'] = {"datefmt": "%Y-%m-%d %H:%M:%S"}
        self.config['output'] = {"format":"json"}
        self.config['data'] = [{"name": "time", "format": "%(asctime)s"}, {"name": "message", "format": "%(message)s"}]

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
        if index is None:
            index = len(self.config['data'])
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

    def log(self, level, message, *args, **kwargs):
        if not self._initialized:
            self._initialize()
        self.logger.log(level, message, *args, **kwargs)

    def _initialize(self):
        if self.root_logger.hasHandlers():
            self.root_logger.removeHandler(self.root_logger.handlers[0])
        self.handler = logging.StreamHandler()
        if self.config['output']['format'] == "json":
            formatter = logging.Formatter("{" + ",".join(['"' + d['name'] + '"' + ":" + '"' + d['format'] +  '"'  for d in self.config['data']]) + "}", **self.config['options'])
        else:
            formatter = logging.Formatter(" ".join(["[" + d['name'] + "=" + d['format'] + "]" for d in self.config['data']]), **self.config['options'])
        self.handler.setFormatter(formatter)
        self.root_logger.addHandler(self.handler)
        self.logger = logging.LoggerAdapter(self.root_logger)


# cl = CustomLogger()
# cl.set_config_data("level", "%(levelname)s", -1)
# cl.set_config_data("process", "%(process)d:%(threadName)s:%(thread)d", -1)
# cl.set_config_data("code", "%(filename)s:%(lineno)d", -1)
# cl.set_config_data("session", "SESSION:123", -1)

# cl.info("hello")
# cl.warn("this is a warning")
