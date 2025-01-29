###### OS / Systems
import datetime
import sys

import pydash

from scheduler import Scheduler

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/utils/")

######
import argparse
import logging
import uuid

###### Parsers, Formats, Utils
import re
import json

###### Backend, Databases
import redis
from redis.commands.json.path import Path

###### Blue
from producer import Producer
from session import Session
from message import Message, MessageType, ContentType, ControlCode
from connection import PooledConnectionFactory
from tracker import PerformanceTracker, Metric, MetricGroup


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


class PlatformPerformanceTracker(PerformanceTracker):
    def __init__(self, platform, properties=None, callback=None):
        self.platform = platform
        super().__init__(prefix=platform.cid, properties=properties, inheritance="perf.platform", callback=callback)

    def collect(self):
        super().collect()

        ### platform group
        platform_group = MetricGroup(id="platform", label="Platform Info", visibility=False)
        self.data.add(platform_group)

        # platform info
        name_metric = Metric(id="name", label="Name", value=self.platform.name, visibility=False)
        platform_group.add(name_metric)
        cid_metric = Metric(id="id", label="ID", value=self.platform.cid, visibility=False)
        platform_group.add(cid_metric)

        ### db group
        db_group = MetricGroup(id="database", label="Database Info")
        self.data.add(db_group)

        ### db connections group
        db_connections_group = MetricGroup(id="database_connections", label="Connections Info")
        db_group.add(db_connections_group)

        connections_factory_id = Metric(id="connection_factory_id", label="Connections Factory ID", type="text", value=self.platform.connection_factory.get_id())
        db_connections_group.add(connections_factory_id)

        # db connection info
        num_created_connections_metric = Metric(id="num_created_connections", label="Num Total Connections", type="series", value=self.platform.connection_factory.count_created_connections())
        db_connections_group.add(num_created_connections_metric)
        num_in_use_connections_metric = Metric(id="num_in_use_connections", label="Num In Use Connections", type="series", value=self.platform.connection_factory.count_in_use_connections())
        db_connections_group.add(num_in_use_connections_metric)
        num_available_connections_metric = Metric(
            id="num_available_connections", label="Num Available Connections", type="series", value=self.platform.connection_factory.count_available_connections()
        )
        db_connections_group.add(num_available_connections_metric)

        return self.data.toDict()


class SessionCleanupScheduler(Scheduler):
    def __init__(self, platform, callback):
        super().__init__(task=self.__session_cleanup)
        self.platform = platform
        self.callback = callback

    def __session_cleanup(self):
        sessions = self.platform.get_sessions()
        deleted_sessions = []
        # TODO: fetch user defined duration under platform metadata session_expiration_duration
        duration = 2
        for session in sessions:
            epoch = pydash.objects.get(session, 'last_activity_date', session['created_date'])
            elapsed = datetime.datetime.now() - datetime.datetime.fromtimestamp(epoch)
            # if no activity for 2 days
            if elapsed.days >= duration:
                self.platform.delete_session(session['id'])
                deleted_sessions.append(session['id'])
        if pydash.is_function(self.callback):
            self.callback(deleted_sessions)

    def set_job(self):
        self.job = self.scheduler.every(10).seconds


class Platform:
    def __init__(self, name="PLATFORM", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        self.connection = None
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

        self._initialize(properties=properties)

        # platform stream
        self.producer = None

        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # tracking for platform
        self.properties['tracker.perf.platform.outputs'] = ["pubsub", "log.INFO"]
        self.properties['tracker.perf.platform.period'] = 30

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### SESSION
    def get_session_sids(self):
        keys = self.connection.keys(pattern=self.cid + ":SESSION:*:DATA")
        keys = "\n".join(keys)
        result = []

        # further apply re to match
        regex = r"SESSION:[^:]*:DATA"

        matches = re.finditer(regex, keys)
        session_sids = [match.group()[:-5] for match in matches]
        return session_sids

    def get_sessions(self):
        session_sids = self.get_session_sids()

        result = []
        for session_sid in session_sids:
            session = self.get_session(session_sid)
            if session is not None:
                result.append(session.to_dict())
        return result

    def get_session(self, session_sid):
        session_sids = self.get_session_sids()

        if session_sid in set(session_sids):
            return Session(sid=session_sid, prefix=self.cid, properties=self.properties)
        else:
            return None

    def create_session(self, created_by=None):
        session = Session(prefix=self.cid, properties=self.properties)
        if not pydash.is_empty(created_by):
            self.set_metadata(f'users.{created_by}.sessions.owner.{session.sid}', True)
        return session

    def delete_session(self, session_sid):
        session_cid = self.cid + ":" + session_sid

        # delete session stream
        self.connection.delete(session_cid + ":STREAM")

        # delete session data, metadata
        self.connection.delete(session_cid + ":DATA")
        self.connection.delete(session_cid + ":METADATA")

        # TODO: delete more

        # TODO: remove, stop all agents

    def _send_message(self, code, params):
        message = {'code': code, 'params': params}
        self.producer.write(data=message, dtype="json", label="INSTRUCTION")

    def join_session(self, session_sid, registry, agent, properties):

        session_cid = self.cid + ":" + session_sid

        args = {}
        args["session"] = session_cid
        args["registry"] = registry
        args["agent"] = agent
        args["properties"] = properties
        self.producer.write_control(ControlCode.JOIN_SESSION, args)

    ###### METADATA RELATED
    def create_update_user(self, user):
        uid = user['uid']
        default_user_role = self.get_metadata('settings.default_user_role')
        if pydash.is_empty(default_user_role):
            default_user_role = 'guest'
        default_user_settings = self.get_metadata('settings.default_user_settings')
        if pydash.is_empty(default_user_settings):
            default_user_settings = {}
        # create user profile with guest role if does not exist
        self.set_metadata(
            f'users.{uid}',
            {
                'uid': user['uid'],
                'role': default_user_role,
                'email': user['email'],
                'name': user['name'],
                'picture': user['picture'],
                'settings': default_user_settings,
                'sessions': {"pinned": {}, "owner": {}, "member": {}},
            },
            nx=True,
        )
        self.set_metadata(f'users.{uid}.email', user['email'])
        self.set_metadata(f'users.{uid}.name', user['name'])
        self.set_metadata(f'users.{uid}.picture', user['picture'])

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
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_metadata_namespace(),
            "$",
            {'users': {}, "settings": {}},
            nx=True,
        )

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    ###### OPERATIONS
    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            producer = Producer(sid="STREAM", prefix=self.cid, properties=self.properties)
            producer.start()
            self.producer = producer

    def perf_tracker_callback(self, data, tracker=None, properties=None):
        pass

    def _init_tracker(self):
        self._tracker = PlatformPerformanceTracker(self, properties=self.properties, callback=lambda *args, **kwargs: self.perf_tracker_callback(*args, **kwargs))

    def _init_session_cleanup_scheduler(self, callback=None):
        self.session_cleanup_scheduler = SessionCleanupScheduler(platform=self, callback=callback)

    def _start_session_cleanup_job(self):
        self.session_cleanup_scheduler.start()

    def _stop_session_cleanup_job(self):
        self.session_cleanup_scheduler.stop()

    def _start_tracker(self):
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        self._tracker.stop()

    def _terminate_tracker(self):
        self._tracker.terminate()

    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.sid))
        self._start_connection()

        # initialize platform metadata
        self._init_metadata_namespace()

        # init tracker
        self._init_tracker()

        # start platform communication stream
        self._start_producer()

        logging.info('Started platform {name}'.format(name=self.sid))

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def stop(self):
        # stop tracker
        self._stop_tracker()


#######################
### EXAMPLE
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", default="INFO", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # create platform
    platform = Platform()

    # list sessions
    sessions = platform.get_sessions()
