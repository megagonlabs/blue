import os
import threading

from datetime import datetime
import time

import json
import logging
import uuid

import psutil
import socket

###### Blue
from blue.stream import Message, MessageType, ContentType
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils


###############
### Metric
#
class Metric:
    """Basic Metric class to configure a metric for tracking"""

    def __init__(self, id=None, label=None, type=None, value=None, visibility=True):
        """Initialize Metric

        Parameters:
            id: Unique identifier for the metric. Defaults to None.
            label: Human-readable label for the metric. Defaults to None.
            type: Type of the metric (e.g., gauge, counter). Defaults to None.
            value: Value of the metric. Defaults to None.
            visibility: Visibility of the metric. Defaults to True.
        """
        self.id = id
        self.label = label
        self.type = type
        self.value = value
        self.visibility = visibility
        self.children = None

    def setValue(self, value):
        """Set the value of the metric

        Parameters:
            value: The value to set for the metric.
        """
        self.value = value

    def getValue(self):
        """
        Get the value of the metric

        Returns:
            The current value of the metric.
        """
        return self.value

    def isVisible(self):
        """Check if the metric is visible

        Returns:
            True if the metric is visible, False otherwise.
        """
        return self.visibility

    def getLabel(self):
        """Get the label of the metric

        Returns:
            The label of the metric.
        """
        return self.label

    def getID(self):
        """Get the ID of the metric

        Returns:
            The ID of the metric.
        """
        return self.id

    def getType(self):
        """Get the type of the metric

        Returns:
            The type of the metric.
        """
        return self.type

    def toDict(self):
        """Convert the metric to a dictionary representation
        Returns:
            A dictionary containing the metric's attributes.
        """
        d = {"id": self.id, "label": self.label, "type": self.type, "visibility": self.visibility}

        d['value'] = self.value

        return d


###############
### MetricGroup
#
class MetricGroup(Metric):
    """MetricGroup class to group multiple metrics together"""

    def __init__(self, id=None, label=None, type="group", visibility=True):
        """
        Initialize MetricGroup

        Parameters:
            id: Unique identifier for the metric group. Defaults to None.
            label: Human-readable label for the metric group. Defaults to None.
            type: Type of the metric group. Defaults to "group".
            visibility: Visibility of the metric group. Defaults to True.
        """
        super().__init__(id=id, label=label, type=type, visibility=visibility)
        self.children = {}

    def add(self, child):
        """
        Add a child metric to the group

        Parameters:
            child: The Metric or MetricGroup to add as a child.
        """
        self.children[child.id] = child

    def getValue(self, path):
        """
        Get the value of a metric by its path

        Parameters:
            path: The dot-separated path to the metric.
        """
        cids = path.split(".")

        c = self
        for index, cid in enumerate(cids):
            if cid in c.children:
                c = c.children[cid]
                if index == len(cids) - 1:
                    return c.getValue()
            else:
                return None

    def toDict(self):
        """
        Convert the metric group to a dictionary representation

        Returns:
            A dictionary containing the metric group's attributes and its children's attributes.
        """
        d = super().toDict()

        d['data'] = {}

        for child_id in self.children:
            d['data'][child_id] = self.children[child_id].toDict()

        return d


###############
### Tracker
#
class Tracker:
    """Basic Tracker class to track and report metrics at regular intervals"""

    def __init__(self, name="TRACKER", id=None, sid=None, cid=None, label=None, prefix=None, suffix=None, properties=None, inheritance=None, callback=None):
        """Initialize Tracker

        Parameters:
            name: Name of the tracker. Defaults to "TRACKER".
            id: Unique identifier for the tracker. If None, a UUID will be generated. Defaults to None.
            sid: Short identifier for the tracker. If None, it will be set to name:id. Defaults to None.
            cid: Canonical identifier for the tracker. If None, it will be set to prefix:sid:suffix. Defaults to None.
            label: Human-readable label for the tracker. Defaults to None.
            prefix: Prefix for the canonical identifier. Defaults to None.
            suffix: Suffix for the canonical identifier. Defaults to None.
            properties: Dictionary of properties to configure the tracker. Defaults to None.
            inheritance: Inheritance string for property inheritance. Defaults to None.
            callback: Optional callback function to be called after tracking. Defaults to None.
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

        self.label = label

        self.callback = callback
        self.timer = None
        self.state = "IDLE"
        self.started = 0
        self.outputs = []

        # init data
        self.data = None

        # init outputs
        self.connection = None

        self.inheritance = inheritance
        self._initialize(properties=properties)

        # auto start, optionally
        self._auto_start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        """
        Initialize tracker properties

        Parameters:
            properties: Dictionary of properties to configure the tracker. Defaults to None.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        """
        Initialize default properties for the tracker.
        """
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
        """
        Update tracker properties

        Parameters:
            properties: Dictionary of properties to configure the tracker. Defaults to None.
        """
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
        """
        Auto-start the tracker if configured to do so.
        """
        if 'tracker.autostart' in self.properties:
            autostart = self.properties['tracker.autostart']
            if autostart:
                self.start()

    def start(self):
        """Start the tracker"""
        self.state = "RUNNING"

        self.started = self.get_current_epoch()

        # create outputs
        outputs = []

        if 'tracker.outputs' in self.properties:
            outputs = self.properties['tracker.outputs']

        if type(outputs) == str:
            outputs = [outputs]

        self.outputs = outputs

        if "pubsub" in set(self.outputs):
            self._start_connection()

        self._run_tracker()

    def _start_connection(self):
        """Start the database connection"""
        if self.connection == None:
            self.connection_factory = PooledConnectionFactory(properties=self.properties)
            self.connection = self.connection_factory.get_connection()

    def stop(self):
        """Stop the tracker"""
        self._stop_tracker()

    def _run_tracker(self):
        """Run the tracker periodically based on the configured period and expiration, if set"""
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
            thread.daemon = True
            self.track()
            thread.start()

    def _stop_tracker(self):
        """Stop the tracker and perform one last tracking operation"""
        # stop and track one last time
        self.state = "STOPPED"
        self.track()

    def terminate(self):
        """Terminate the tracker immediately"""
        self._terminate_tracker()

    def _terminate_tracker(self):
        """Terminate the tracker immediately"""
        # terminate immediately
        try:
            self.timer.cancel()
        except Exception as ex:
            print(ex)

    def get_current_epoch(self):
        """Get the current epoch time in seconds

        Returns:
            Current epoch time in seconds as an integer.
        """
        return int(time.time())

    def getValue(self, path):
        """Get the value of a metric by its path

        Parameters:
            path: The path of the metric to retrieve.
        """
        if self.data:
            return self.data.getValue(path)

        return None

    def collect(self):
        """Collect tracker metrics such as current and started time, process id, status and return as a dictionary"""
        ## top level tracker results
        self.data = MetricGroup(id=self.cid, label=self.label, type="tracker")

        ## tracker metadata
        tracker_metadata_group = MetricGroup(id="metadata", label="Tracker Info")
        self.data.add(tracker_metadata_group)

        # current time
        current_time_metric = Metric(id="current", label="Current Time", type="time", value=self.get_current_epoch())
        tracker_metadata_group.add(current_time_metric)
        # started time
        started_time_metric = Metric(id="started", label="Started Time", type="time", value=self.started, visibility=False)
        tracker_metadata_group.add(started_time_metric)
        # pid
        process_id_metric = Metric(id="pid", label="Process Id", type="number", value=os.getpid(), visibility=False)
        tracker_metadata_group.add(process_id_metric)
        # state
        state_metric = Metric(id="status", label="Status", type="status", value=self.state)
        tracker_metadata_group.add(state_metric)

        return self.data.toDict()

    def track(self):
        """Track and report the collected metrics to the configured outputs"""
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
            elif output == "pubsub":
                self.connection.publish(self.cid, json.dumps(data))

        # additional callback
        if self.callback:
            self.callback(data, tracker=self, properties=self.properties)


###############
### IdleTracker
#
class IdleTracker(Tracker):
    """IdleTracker to monitor consumer activity and report last active time"""

    def __init__(self, consumer, properties=None, callback=None):
        """Initialize IdleTracker

        Parameters:
            consumer: The consumer object to monitor.
            properties: Dictionary of properties to configure the tracker. Defaults to None.
            callback: Optional callback function to be called after tracking. Defaults to None.
        """
        self.consumer = consumer
        super().__init__(id="IDLE", prefix=consumer.sid, properties=properties, inheritance="idle.consumer", callback=callback)

    def _initialize_properties(self):
        """
        Initialize default properties for the IdleTracker.
        """
        super()._initialize_properties()

        # tracking defaults
        self.properties['tracker.idle.autostart'] = True
        self.properties['tracker.idle.outputs'] = []
        self.properties['tracker.idle.period'] = 60

    def collect(self):
        """
        Collect IdleTracker metrics including last active time and return as a dictionary

        Returns:
            A dictionary containing the collected metrics.
        """
        super().collect()

        # add last active time
        last_active_metric = Metric(id="last_active", label="Last Active Time", type="time", value=self.consumer.last_processed)
        self.data.add(last_active_metric)

        return self.data.toDict()


######################
### PerformanceTracker
#
class PerformanceTracker(Tracker):
    """PerformanceTracker to monitor thread and system performance metrics"""

    def __init__(self, label=None, prefix=None, properties=None, inheritance=None, callback=None):
        """Initialize PerformanceTracker

        Parameters:
            label: Human-readable label for the tracker. Defaults to None.
            prefix: Prefix for the group. Defaults to None.
            properties: Dictionary of properties to configure the tracker. Defaults to None.
            inheritance: Inheritance string for property inheritance. Defaults to None.
            callback: Optional callback function to be called after tracking. Defaults to None.
        """
        super().__init__(id="PERF", label=label, prefix=prefix, properties=properties, inheritance=inheritance, callback=callback)

    def collect(self):
        """Collect PerformanceTracker metrics including thread and system performance and return as a dictionary"""
        super().collect()

        ### Thread group
        thread_group = MetricGroup(id="threads_info", label="Threads Info")
        self.data.add(thread_group)

        # num threads
        num_threads_metric = Metric(id="num_threads", label="Thread Count", type="number", value=threading.active_count())
        thread_group.add(num_threads_metric)

        thread_list_group = MetricGroup(id="threads_list", label="Threads List", type="list")
        thread_group.add(thread_list_group)

        # thread list
        for thread in threading.enumerate():
            id = thread.ident
            label = thread.name
            daemon = thread.isDaemon()
            alive = thread.is_alive()

            thread_metric_group = MetricGroup(id=id, label=label)
            thread_list_group.add(thread_metric_group)

            is_daemon_metric = Metric(id="daemon", label="Daemon", type="tag", value=daemon)
            thread_metric_group.add(is_daemon_metric)

            is_alive_metric = Metric(id="alive", label="Alive", type="alive", value=alive)
            thread_metric_group.add(is_alive_metric)

        return self.data.toDict()


############################
### SystemPerformanceTracker
#
class SystemPerformanceTracker(Tracker):
    """SystemPerformanceTracker to monitor system performance metrics such as CPU, memory, and processes"""

    def __init__(self, label=None, properties=None, callback=None):
        """Initialize SystemPerformanceTracker

        Parameters:
            label: Human-readable label for the tracker. Defaults to None.
            properties: Dictionary of properties to configure the tracker. Defaults to None.
            callback: Optional callback function to be called after tracking. Defaults to None.
        """
        platform_id = "UNKNOWN"
        if properties and "platform.name" in properties:
            platform_id = properties["platform.name"]
        super().__init__(id="PERF", label=label, prefix="PLATFORM:" + platform_id + ":SYSTEM:" + socket.gethostname(), properties=properties, inheritance="perf.system", callback=callback)

    def collect(self):
        """Collect SystemPerformanceTracker metrics such as CPU, memory, and processes and return as a dictionary"""
        super().collect()

        ### CPU group
        cpu_group = MetricGroup(id="cpu_info", label="CPU Info")
        self.data.add(cpu_group)

        # cpu
        cpu_percent_metric = Metric(id="cpu_percent", label="Percent CPU Use", type="series", value=psutil.cpu_percent())
        cpu_group.add(cpu_percent_metric)
        cpu_count_metric = Metric(id="cpu_count", label="CPU Count", type="number", value=psutil.cpu_count(), visibility=False)
        cpu_group.add(cpu_count_metric)

        cpu_load = psutil.getloadavg()
        cpu_load_metric = Metric(id="cpu_load", label="CPU Load Per Min", type="number", value=cpu_load[0], visibility=False)
        cpu_group.add(cpu_load_metric)

        cpu_times = psutil.cpu_times()
        cpu_times_user_metric = Metric(id="cpu_times_user", label="CPU Time (user)", type="number", value=cpu_times.user, visibility=False)
        cpu_group.add(cpu_times_user_metric)
        cpu_times_system_metric = Metric(id="cpu_times_system", label="CPU Time (system)", type="number", value=cpu_times.system, visibility=False)
        cpu_group.add(cpu_times_system_metric)
        cpu_times_idle_metric = Metric(id="cpu_times_idle", label="CPU Time (idle)", type="number", value=cpu_times.idle, visibility=False)
        cpu_group.add(cpu_times_idle_metric)

        ### Memory group
        memory_group = MetricGroup(id="memory_info", label="Memory Info")
        self.data.add(memory_group)

        # memory
        virtual_memory = psutil.virtual_memory()
        virtual_memory_total_metric = Metric(id="virtual_memory_total", label="Virtual Memory (total)", type="number", value=virtual_memory.total)
        memory_group.add(virtual_memory_total_metric)
        virtual_memory_available_metric = Metric(id="virtual_memory_available", label="Virtual Memory (avail)", type="number", value=virtual_memory.available)
        memory_group.add(virtual_memory_available_metric)
        virtual_memory_used_metric = Metric(id="virtual_memory_used", label="Virtual Memory (used)", type="number", value=virtual_memory.used, visibility=False)
        memory_group.add(virtual_memory_used_metric)
        virtual_memory_free_metric = Metric(id="virtual_memory_free", label="Virtual Memory (free)", type="number", value=virtual_memory.free, visibility=False)
        memory_group.add(virtual_memory_free_metric)
        virtual_memory_percent_metric = Metric(id="virtual_memory_percent", label="Virtual Memory (%)", type="series", value=virtual_memory.percent)
        memory_group.add(virtual_memory_percent_metric)

        ### Process group
        processes_group = MetricGroup(id="processes_info", label="Processes Info")
        self.data.add(processes_group)

        # num processes
        pids = psutil.pids()
        num_processes_metric = Metric(id="num_processes", label="Process Count", type="number", value=len(pids))
        processes_group.add(num_processes_metric)

        process_list_group = MetricGroup(id="process_list", label="Process List", type="list")
        processes_group.add(process_list_group)

        for pid in pids:
            try:
                process = psutil.Process(pid)

                process_group = MetricGroup(id="process_" + str(pid), label="Process Details")
                process_list_group.add(process_group)

                ### metadata group
                process_metadata_group = MetricGroup(id="metadata", label="Process Metadata")
                process_group.add(process_metadata_group)

                # pid
                pid_metric = Metric(id="pid", label="Process ID", type="number", value=pid)
                process_metadata_group.add(pid_metric)
                # name
                name_metric = Metric(id="name", label="Process Name", type="text", value=process.name())
                process_metadata_group.add(name_metric)
                # status
                status_metric = Metric(id="status", label="Process Status", type="status", value=process.status())
                process_metadata_group.add(status_metric)
                # started
                started_metric = Metric(id="started", label="Started Time", type="time", value=int(process.create_time()), visibility=False)
                process_metadata_group.add(started_metric)

                ### cpu group
                process_cpu_group = MetricGroup(id="cpu", label="CPU Info", visibility=False)
                process_group.add(process_cpu_group)

                # cpu percent
                process_cpu_percent_metric = Metric(id="cpu_percent", label="Percent CPU Use", type="number", value=process.cpu_percent(), visibility=False)
                process_cpu_group.add(process_cpu_percent_metric)

                # cpu num
                process_cpu_num_metric = Metric(id="cpu_num", label="CPU Count", type="number", value=process.cpu_num(), visibility=False)
                process_cpu_group.add(process_cpu_num_metric)

                # cpu times user
                cpu_times = process.cpu_times()
                process_cpu_times_user_metric = Metric(id="cpu_times_user", label="CPU Time (user)", type="number", value=cpu_times.user, visibility=False)
                process_cpu_group.add(process_cpu_times_user_metric)
                process_cpu_times_system_metric = Metric(id="cpu_times_system", label="CPU Time (system)", type="number", value=cpu_times.system, visibility=False)
                process_cpu_group.add(process_cpu_times_system_metric)

                ### memory group
                process_memory_group = MetricGroup(id="memory", label="Memory Info", visibility=False)
                process_group.add(process_memory_group)

                # memory percent
                process_memory_percent_metric = Metric(id="memory_percent", label="Process Memory (%)", type="series", value=process.memory_percent(), visibility=False)
                process_memory_group.add(process_memory_percent_metric)

                memory_info = process.memory_info()
                process_memory_rss_metric = Metric(id="memory_rss", label="Process Memory (rss)", type="number", value=memory_info.rss, visibility=False)
                process_memory_group.add(process_memory_rss_metric)
                process_memory_vms_metric = Metric(id="memory_vms", label="Process Memory (vms)", type="number", value=memory_info.vms, visibility=False)
                process_memory_group.add(process_memory_vms_metric)
                process_memory_shared_metric = Metric(id="memory_shared", label="Process Memory (shared)", type="number", value=memory_info.shared, visibility=False)
                process_memory_group.add(process_memory_shared_metric)

                ### thread group
                process_thread_group = MetricGroup(id="threads", label="Process Thread Info", visibility=False)
                process_group.add(process_thread_group)

                #  process num threads
                process_num_threads_metric = Metric(id="num_threads", label="Thread Count", type="number", value=process.num_threads(), visibility=False)
                process_thread_group.add(process_num_threads_metric)

                # threads = process.threads()
                # for thread in threads:
                #     thread_info = {"id": thread.id, "user_time": thread.user_time, "system_time": thread.system_time}

            except:
                continue

        return self.data.toDict()
