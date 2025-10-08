###### Parsers, Formats, Utils
import logging
import time
import json
import pydash

##### Communication
import asyncio
import websockets


###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.connection import PooledConnectionFactory
from blue.tracker import Tracker, Metric, MetricGroup
from blue.utils import uuid_utils, log_utils

# service tracker
service_tracker = None

# system tracker
system_tracker = None


class ServicePerformanceTracker(Tracker):
    """Tracker for monitoring service performance metrics such as call count, average call length, and average response time."""

    def __init__(self, service, properties=None, callback=None):
        """Initialize the ServicePerformanceTracker.

        Parameters:
            service: The service instance to track.
            properties: Optional properties for the tracker. Defaults to None.
            callback: Optional callback function to be called on data collection. Defaults to None.
        """
        self.service = service
        super().__init__(id="PERF", prefix=service.cid, properties=properties, inheritance="perf.service", callback=callback)

    def collect(self):
        """Collect performance metrics and return them as a dictionary. Performance metrics include call count, average call length, and average response time.

        Returns:
            Dictionary containing collected performance metrics.
        """
        super().collect()

        ### cost group
        service_cost_group = MetricGroup(id="service_cost_group", label="Service Cost Info")
        self.data.add(service_cost_group)

        ### response_time group
        service_response_time_group = MetricGroup(id="service_response_time_group", label="Service Response Time Info")
        self.data.add(service_response_time_group)

        ### service group
        service_group = MetricGroup(id="service_info", label="Service Info")
        self.data.add(service_group)

        ### num calls
        # get previous total count
        total_call_count = self.service.get_metadata("stats.total_call_count")
        if total_call_count is None:
            total_call_count = 0

        # get previous average length
        avg_call_length = self.service.get_metadata("stats.avg_call_length")
        if avg_call_length is None:
            avg_call_length = 0
        total_call_length = avg_call_length * total_call_count

        # get previous average response time
        avg_response_time = self.service.get_metadata("stats.avg_response_time")
        if avg_response_time is None:
            avg_response_time = 0
        total_call_response_time = avg_response_time * total_call_count

        # calculate new calls
        socket_stats = self.service.get_metadata("stats.websockets")
        new_call_count = 0

        if socket_stats:
            for socket_id in socket_stats:
                new_call_count += 1

                # length
                length = self.service.get_metadata("stats.websockets." + str(socket_id) + "." + "length")
                if length is None:
                    length = 0
                total_call_length += length

                # response time
                response_time = self.service.get_metadata("stats.websockets." + str(socket_id) + "." + "response_time")
                if response_time is None:
                    response_time = 0
                total_call_response_time += response_time

                # delete
                self.service.delete_metadata("stats.websockets." + socket_id)

        # write total count
        total_call_count = total_call_count + new_call_count
        self.service.set_metadata("stats.total_call_count", total_call_count)

        # average length
        if total_call_count > 0:
            avg_call_length = total_call_length / total_call_count
        else:
            avg_call_length = 0.0
        self.service.set_metadata("stats.avg_call_length", avg_call_length)

        # average response time
        if total_call_count > 0:
            avg_response_time = total_call_response_time / total_call_count
        else:
            avg_response_time = 0.0
        self.service.set_metadata("stats.avg_response_time", avg_response_time)

        num_calls_metric = Metric(id="num_calls", label="Call Count", type="number", value=total_call_count)
        service_cost_group.add(num_calls_metric)

        avg_call_length_metric = Metric(id="avg_call_length", label="Average Call Length", type="series", value=avg_call_length)
        service_cost_group.add(avg_call_length_metric)

        aavg_response_time_metric = Metric(id="avg_response_time", label="Average Response Time", type="series", value=avg_response_time)
        service_response_time_group.add(aavg_response_time_metric)

        return self.data.toDict()


class Service:
    """Service class for handling communication with external APIs."""

    def __init__(
        self,
        name="SERVICE",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        handler=None,
        properties={},
    ):
        """Initialize the Service.

        Parameters:
            name: Name of the service. Defaults to "SERVICE".
            id: Unique identifier for the service. Defaults to None.
            sid: Short identifier for the service. Defaults to None.
            cid: Canonical identifier for the service. Defaults to None.
            prefix: Optional prefix for the cid. Defaults to None.
            suffix: Optional suffix for the cid. Defaults to None.
            handler: Callback function to handle service requests. Defaults to None.
            properties: Additional properties for the service. Defaults to {}.
        """
        self.name = name
        if id:
            self.id = id
        else:
            self.id = uuid_utils.create_uuid()

        if sid:
            self.sid = sid
        else:
            self.sid = self.name + ":" + self.id

        self.prefix = prefix
        self.suffix = suffix
        self.cid = cid

        if self.cid == None:
            self.cid = self.sid

            if self.prefix:
                self.cid = self.prefix + ":" + self.cid
            if self.suffix:
                self.cid = self.cid + ":" + self.suffix

        self._initialize(properties=properties)

        # override, if necessary
        if handler is not None:
            self.handler = lambda *args, **kwargs: handler(*args, **kwargs, properties=self.properties)
        else:
            self.handler = lambda *args, **kwargs: self.default_handler(*args, **kwargs, properties=self.properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """Initialize the service with properties.

        Parameters:
            properties: Additional properties for the service. Defaults to None.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize default properties for the service."""
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # stats tracker
        self.properties["tracker.perf.service.autostart"] = True
        self.properties["tracker.perf.service.outputs"] = ["pubsub"]

    def _update_properties(self, properties=None):
        """Update service properties with provided properties.

        Parameters:
            properties: Additional properties for the service. Defaults to None.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        """Initialize the logger for the service."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("service", self.sid, -1)

    ###### database, data
    def _start_connection(self):
        """Start the database connection using a pooled connection factory."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ##### tracker
    def stat_tracker_callback(self, data, tracker=None, properties=None):
        """Callback function for service performance tracking."""
        pass

    def _init_tracker(self):
        """Initialize the service performance tracker."""
        # service stat tracker
        self._tracker = ServicePerformanceTracker(self, properties=self.properties, callback=lambda *args, **kwargs: self.stat_tracker_callback(*args, **kwargs))

    def _start_tracker(self):
        """Start the service performance tracker."""
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        """Stop the service performance tracker."""
        self._tracker.stop()

    def _terminate_tracker(self):
        """Terminate the service performance tracker."""
        self._tracker.terminate()

    ## service metadata
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

    def _init_metadata_namespace(self):
        """Initialize the metadata namespace for the service, sets created_date and initializes key stats for websockets and total call count."""
        # create namespaces for metadata
        self.connection.json().set(
            self._get_metadata_namespace(),
            "$",
            {"stats": {}},
            nx=True,
        )

        # add created_date
        self.set_metadata("created_date", int(time.time()), nx=True)

        # websockers
        self.set_metadata("stats.websockets", {}, nx=True)

        # total call count
        self.set_metadata("stats.total_call_count", int(0), nx=True)

    def _get_metadata_namespace(self):
        """Get the metadata namespace for the service."""
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        """Set metadata for the service.

        Parameters:
            key: Metadata key to set.
            value: Value to set for the metadata key.
            nx: If True, set the value only if the key does not already exist. Defaults to False.
        """
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def delete_metadata(self, key):
        """Delete metadata for the service.

        Parameters:
            key: Metadata key to delete.
        """
        self.connection.json().delete(self._get_metadata_namespace(), "$." + key)

    def get_metadata(self, key=""):
        """Get metadata for the service.

        Parameters:
            key: Metadata key to retrieve. Defaults to "".
        Returns:
            Value of the metadata key, or None if the key does not exist.
        """
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    def _init_socket_stats(self, websocket):
        """Initialize socket statistics for a given websocket connection.

        Parameters:
            websocket: WebSocket connection object.
        """
        # stats by websocket.id
        wsid = websocket.id
        self.set_metadata("stats.websockets." + str(wsid), {}, nx=True)

        self.set_socket_stat(websocket, "created_date", int(time.time()), nx=True)

    def set_socket_stat(self, websocket, key, value, nx=False):
        """Set a specific statistic for a given websocket connection.

        Parameters:
            websocket: WebSocket connection object.
            key: Statistic key to set.
            value: Value to set for the statistic key.
            nx: If True, set the value only if the key does not already exist. Defaults to False.
        """
        wsid = websocket.id
        self.set_metadata("stats.websockets." + str(wsid) + "." + key, value, nx=True)

    ###### handlers
    async def _handler(self, websocket):
        """Handle incoming WebSocket messages and process them using the service's handler function.
        Sets up socket statistics and processes messages in a loop until the connection is closed.

        Parameters:
            websocket: WebSocket connection object.
        """
        self._init_socket_stats(websocket)

        while True:
            try:
                ### read message
                s = await websocket.recv()

                # message length
                self.set_socket_stat(websocket, "length", len(s))

                message = json.loads(s)

                ### process message
                start = time.time()
                response = self.handler(message, websocket=websocket)
                end = time.time()
                self.set_socket_stat(websocket, "response_time", end - start)

                ### write response
                await websocket.send(response.json())

            except websockets.ConnectionClosedOK:
                break

    async def start_listening_socket(self):
        """Start listening for incoming WebSocket connections on port 8001."""
        async with websockets.serve(self._handler, "", 8001):
            await asyncio.Future()  # run forever

    ## default handler, override
    def default_handler(self, message, properties=None, websocket=None):
        """Default handler for processing incoming messages. This method should be overridden by subclasses to implement custom behavior.

        Parameters:
            message: Incoming message to process.
            properties: Additional properties for the handler. Defaults to None.
            websocket: WebSocket connection object. Defaults to None.
        Returns:
            Response message. Should be overridden to provide meaningful responses.
        """
        self.logger.info("default_handler: override")

    def _start(self):
        """Start the service by establishing a database connection, initializing metadata, and starting the performance tracker if configured."""
        self._start_connection()

        # initialize session metadata
        self._init_metadata_namespace()

        # init tracker
        self._init_tracker()

        self.logger.info("Started service {name}".format(name=self.name))

    def stop(self):
        """Stop the service by stopping and terminating the performance tracker."""
        self.logger.info("Stopped servie {name}".format(name=self.name))
