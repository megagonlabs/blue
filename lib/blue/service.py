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
from blue.utils import uuid_utils



# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


# service tracker
service_tracker = None

# system tracker
system_tracker = None


class ServicePerformanceTracker(Tracker):
    def __init__(self, service, properties=None, callback=None):
        self.service = service
        super().__init__(id="PERF", prefix=service.cid, properties=properties, inheritance="perf.service", callback=callback)

    def collect(self):
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
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # stats tracker
        self.properties["tracker.perf.service.autostart"] = True
        self.properties["tracker.perf.service.outputs"] = ["pubsub"]

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ##### tracker
    def stat_tracker_callback(self, data, tracker=None, properties=None):
        pass

    def _init_tracker(self):
        # service stat tracker
        self._tracker = ServicePerformanceTracker(self, properties=self.properties, callback= lambda *args, **kwargs: self.stat_tracker_callback(*args, **kwargs) )

    def _start_tracker(self):
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        self._tracker.stop()

    def _terminate_tracker(self):
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
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def delete_metadata(self, key):
        self.connection.json().delete(self._get_metadata_namespace(), "$." + key)

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)
    
    def _init_socket_stats(self, websocket):
        # stats by websocket.id
        wsid = websocket.id
        self.set_metadata("stats.websockets." + str(wsid), {}, nx=True)

        self.set_socket_stat(websocket, "created_date", int(time.time()), nx=True)


    def set_socket_stat(self, websocket, key, value, nx=False):
        wsid = websocket.id
        self.set_metadata("stats.websockets." + str(wsid) + "." + key, value, nx=True)

    ###### handlers
    async def _handler(self, websocket):
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
                self.set_socket_stat(websocket, "response_time", end-start)

                ### write response
                await websocket.send(response.json())

            except websockets.ConnectionClosedOK:
                break

    async def start_listening_socket(self):
        async with websockets.serve(self._handler, "", 8001):
            await asyncio.Future()  # run forever

    ## default handler, override
    def default_handler(self, message, properties=None, websocket=None):
        logging.info("default_handler: override")


    def _start(self):
        self._start_connection()

       
        # initialize session metadata
        self._init_metadata_namespace()

        # init tracker
        self._init_tracker()


        logging.info("Started service {name}".format(name=self.name))

    def stop(self):
        logging.info("Stopped servie {name}".format(name=self.name))
        