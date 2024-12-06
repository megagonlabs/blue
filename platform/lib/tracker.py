
import os
import threading

from datetime import datetime
import time    

import json
import logging

class Tracker:

    def __init__(self, id, properties=None, callback=None):
        self.id = id
        self.properties = properties
        self.callback = callback
        
        self.state = "IDLE"

    def start(self):
        self.state = "RUNNING"
        self._run_tracker()

    def stop(self):
        self._stop_tracker()

    def _run_tracker(self):
        if self.state == "RUNNING":
            thread = threading.Timer(60.0, lambda: self._run_tracker())
            thread.name = "Thread-" + self.__class__.__name__ + "-" + self.id
            thread.start()
            self.track()

    def _stop_tracker(self):
        self.state = "IDLE"

    def collect(self):
        return {
            "id": self.id,
            "pid": os.getpid(),
            "epoch": int(time.time()),
            "date": str(datetime.now())
        }
    
    def track(self):
        data = self.collect()

        # output tracking data, default "system"
        output = "system"
        if 'tracker.output' in self.properties:
            output = self.properties['tracker.output']
       
        if output == "system" or output.find("log") == 0:
            indent = None
            if 'tracker.output.indent' in self.properties:
                indent = self.properties['tracker.output.indent']

            if output == "system":
                print(json.dumps(data, indent=indent))
            else:
                level = output.split(".")[1:]
                if len(level) == 0:
                    level = logging.DEBUG
                else:
                    level = level[0].upper()
                    level = getattr(logging, level)
                
                logging.log(level, json.dumps(data, indent=indent))
        else:
            if self.callback:
                self.callback(data)

class PerformanceTracker(Tracker):
    def __init__(self, name, properties=None, callback=None):
        super().__init__(name, properties=properties, callback=callback)

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
            data["threads"][id] = { "name": name, "id": id, "daemon": daemon, "alive": alive}
    
        return data

