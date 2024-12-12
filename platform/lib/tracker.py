import os
import threading

from datetime import datetime
import time

import json
import logging
import uuid

###### Blue
from producer import Producer
from message import Message, MessageType, ContentType, ControlCode
from connection import PooledConnectionFactory

class Tracker:

    def __init__(self, name="TRACKER", id=None, sid=None, cid=None, prefix=None, suffix=None, properties=None, inheritance=None, callback=None):

        self.name = name
        if id:
            self.id = id
        else:
            self.id = str(hex(uuid.uuid4().fields[0]))[2:]

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

        self.callback = callback
        self.timer = None
        self.state = "IDLE"

        # init outputs
        self.connection = None
        self._producer = None

        self.inheritance = inheritance
        self._initialize(properties=properties)

        # auto start, optionally
        self._auto_start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # tracking defaults
        self.properties['tracker.autostart'] = False
        self.properties['tracker.outputs'] = []
        self.properties['tracker.output.indent'] = None
        self.properties['tracker.period'] = 60
        self.properties['tracker.expiration'] = None

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

        # inherit properties
        inheritance = self.inheritance
        if inheritance is None:
            inheritance = []
        else:
            inheritance = inheritance.split(".")

        inherited_properties = ["autostart", "outputs", "output.indent", "period", "expiration"]

        # inherit properties from inheritance
        path = "tracker"
        for parent in inheritance:
            pp = path + "." + parent 
            for inherited_property in inherited_properties:
                to_p = "tracker" + "." + inherited_property
                from_p = pp + "." + inherited_property
                if from_p in self.properties:
                    self.properties[to_p] = self.properties[from_p]
            path = pp


    def _auto_start(self):
        if 'tracker.autostart' in self.properties:
            autostart = self.properties['tracker.autostart']
            if autostart:
                self.start()

    def start(self):
        self.state = "RUNNING"

        self.started = self.get_current_epoch()

        # create outputs
        outputs = []
    
        if 'tracker.outputs' in self.properties:
            outputs = self.properties['tracker.outputs']

        if type(outputs) == str:
            outputs = [outputs]

        self.outputs = outputs
        
        if "stream" in set(self.outputs):
            self._start_connection()
            # create stream producer
            self._producer = Producer(
                cid=self.id,
                properties=self.properties,
            )
            self._producer.start()

        if "pubsub" in set(self.outputs):
            self._start_connection()

        self._run_tracker()

    def _start_connection(self):
        if self.connection == None:
            self.connection_factory = PooledConnectionFactory(properties=self.properties)
            self.connection = self.connection_factory.get_connection()

    def stop(self):
        self._stop_tracker()

    def _run_tracker(self):

        period = None
        if 'tracker.period' in self.properties:
            period = self.properties['tracker.period']

        expiration = None
        if 'tracker.expiration' in self.properties:
            expiration = self.properties['tracker.expiration']

        if expiration:
            current = self.get_current_epoch()

            if current > self.started + expiration:
                # expire and track one last time
                self.state = "EXPIRED"
                self.track()

        if period and self.state == "RUNNING":
            self.timer = thread = threading.Timer(period, lambda: self._run_tracker())
            thread.name = "Thread-" + self.__class__.__name__ + "-" + self.cid
            self.track()
            thread.start()

    def _stop_tracker(self):
        # stop and track one last time
        self.state = "STOPPED"
        self.track()

    def terminate(self):
        self._terminate_tracker()

    def _terminate_tracker(self):
        # terminate immediately
        try:
            self.timer.cancel()
        except Exception as ex:
            print(ex)

    def get_current_epoch(self):
        return int(time.time())
    
    def collect(self):
        return { "id": self.id, "name": self.name, "cid": self.cid, "pid": os.getpid(), "state": self.state, "epoch": self.get_current_epoch(), "started": self.started }

    def track(self):
        data = self.collect()

        if 'tracker.output.indent' in self.properties:
            indent = self.properties['tracker.output.indent']

        for output in self.outputs:
            if output == "system":
                print(json.dumps(data, indent=indent))
            elif output.find("log") == 0:
                level = output.split(".")[1:]
                if len(level) == 0:
                    level = logging.DEBUG
                else:
                    level = level[0].upper()
                    level = getattr(logging, level)

                logging.log(level, json.dumps(data, indent=indent))
            elif output == "stream":
                # create a message
                message = Message(MessageType.DATA, data, ContentType.JSON)
                self._producer.write(message)
            elif output == "pubsub":
                self.connection.publish(self.cid, json.dumps(data))

        # additional callback
        if self.callback:
            self.callback(data, properties=self.properties)


class PerformanceTracker(Tracker):
    def __init__(self, prefix=None, properties=None, inheritance=None, callback=None):
        super().__init__(id="PERF", prefix=prefix, properties=properties, inheritance=inheritance, callback=callback)

    def collect(self):
        data = super().collect()

        # add num threads
        data["num_threads"] = threading.active_count()

        # thread info
        data["threads"] = {}
        for thread in threading.enumerate():
            id = thread.ident
            name = thread.name
            daemon = thread.isDaemon()
            alive = thread.is_alive()
            data["threads"][id] = {"name": name, "id": id, "daemon": daemon, "alive": alive}

        return data
