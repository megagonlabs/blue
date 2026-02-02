import functools, inspect
import pydash
import time
from redlock import Redlock
from blue.connection import PooledConnectionFactory


class Bluelock:
    def __init__(self, properties):
        self.host = pydash.objects.get(properties, 'db.host', 'blue_db_redis')
        self.port = pydash.objects.get(properties, 'db.port', '6379')
        self.db = pydash.objects.get(properties, 'db.db', 0)
        # redlock for the mutex on the index
        self.retry_count = pydash.objects.get(properties, 'retry_count', 3)
        self.retry_delay = pydash.objects.get(properties, 'retry_delay', 1)

        self.redlock_client = Redlock([{"host": self.host, "port": self.port, "db": self.db}], retry_count=self.retry_count, retry_delay=self.retry_delay)
        self.connection_factory = PooledConnectionFactory(properties=properties)
        self.connection = self.connection_factory.get_connection()

        platform_id = pydash.objects.get(properties, "platform.name", "default")
        self.prefix = ":".join(["PLATFORM", platform_id, "BLUELOCK"])
        self.resource = 'BLUEPRINT'

    def __lock_tree_mutex(self):
        # lock time in milliseconds
        # ops for locking/checking/updating/releasing resource tree should be done within 1 second
        return self.redlock_client.lock(f'{self.prefix}:MUTEX:{self.resource}', 1000)

    # expiration in seconds
    def lock(self, path, expiration=10):
        locked = False
        tree_mutex = self.__lock_tree_mutex(self.resource)
        if not tree_mutex:
            return False
        try:
            # normalize path (a.b -> a:b)
            lock_path = path.replace(".", ":")
            # define Keys
            full_lock_key = f'{self.prefix}:LOCK:{self.resource}:{lock_path}'
            index_key = f'{self.prefix}:INDEX:{self.resource}'
            conflict = False
            # check ancestors
            # e.g. locking "a:b:c", check "a", then "a:b"
            parts = lock_path.split(":")
            for i in range(len(parts) - 1):
                ancestor = ":".join(parts[: i + 1])
                if self.connection.sismember(index_key, ancestor):
                    # cleanup check
                    ancestor_lock_key = f'{self.prefix}:LOCK:{self.resource}:{ancestor}'
                    if not self.connection.exists(ancestor_lock_key):
                        self.connection.srem(index_key, ancestor)
                    else:
                        conflict = True
                        break
            if conflict:
                return False
            # check descendants
            # e.g. locking "a", check if "a:b" exists
            # SSCAN is non-blocking
            cursor = '0'
            while cursor != 0:
                cursor, active_locks = self.connection.sscan(index_key, cursor=cursor, match=f'{lock_path}:*')
                for child in active_locks:
                    # cleanup
                    child_lock_key = f'{self.prefix}:LOCK:{self.resource}:{child}'
                    if not self.connection.exists(child_lock_key):
                        self.connection.srem(index_key, child)
                    else:
                        conflict = True
                        break
                if conflict:
                    break
            # check exact match
            if not conflict:
                if self.connection.exists(full_lock_key):
                    conflict = True

            # apply lock
            if not conflict:
                pipe = self.connection.pipeline()
                # set the lock with TTL
                pipe.set(full_lock_key, 1, ex=expiration)
                # add to index map
                pipe.sadd(index_key, lock_path)
                pipe.execute()
                locked = True
        finally:
            # always release the traffic cop
            self.redlock_client.unlock(tree_mutex)
        return locked

    def __get_arg_values(self, func, *args, **kwargs):
        signature = inspect.signature(func)
        bound_arguments = signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        return bound_arguments.arguments

    # decorator (helper)
    def with_json_lock(self, expiration=10, timeout=5, namespace_param="namespace", key_param="key", namespace_value=None, key_value=None):
        def with_args(task_func):
            @functools.wraps(task_func)
            def wrapper(*args, **kwargs):
                # map arguments
                arg_values = self.__get_arg_values(task_func, *args, **kwargs)
                if namespace_value is not None:
                    actual_namespace = namespace_value
                else:
                    if namespace_param not in arg_values:
                        raise ValueError(f"Function decorated with_json_lock must have '{namespace_param}' argument or explicit 'namespace_value'")
                    actual_namespace = arg_values[namespace_param]
                if key_value is not None:
                    actual_key = key_value
                else:
                    if key_param not in arg_values:
                        raise ValueError(f"Function decorated with_json_lock must have '{key_param}' argument or explicit 'key_value'")
                    actual_key = arg_values[key_param]
                path = f'{actual_namespace}:{actual_key}'
                # busy wait (with timeout)
                start_time = time.time()
                locked = False
                while (time.time() - start_time) < timeout:
                    if self.lock(self.resource, path, expiration):
                        locked = True
                        break
                    time.sleep(0.2)
                if not locked:
                    raise Exception(f"Could not acquire lock for {self.resource}:{path} within {timeout} second{'s' if timeout > 1 else ''}")
                # execute function and ensure unlock
                try:
                    return task_func(*args, **kwargs)
                finally:
                    self.unlock(self.resource, path)

            return wrapper

        return with_args

    def unlock(self, path):
        lock_path = path.replace(".", ":")
        full_lock_key = f'{self.prefix}:LOCK:{self.resource}:{lock_path}'
        index_key = f'{self.prefix}:INDEX:{self.resource}'
        tree_mutex = self.__lock_tree_mutex(self.resource)
        if tree_mutex:
            try:
                pipe = self.connection.pipeline()
                pipe.delete(full_lock_key)
                pipe.srem(index_key, lock_path)
                pipe.execute()
            finally:
                self.redlock_client.unlock(tree_mutex)
