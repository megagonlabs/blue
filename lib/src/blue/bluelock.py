import functools, inspect
from redis import ConnectionPool, Redis
import pydash
import time
from redlock import Redlock


class Bluelock:
    def __init__(self, properties):
        self.host = pydash.objects.get(properties, ['db.host'], None)
        self.port = pydash.objects.get(properties, ['db.port'], None)
        self.db = pydash.objects.get(properties, ['db.db'], None)

        # for obtaining lock on the resource tree
        self.retry_count = pydash.objects.get(properties, 'retry_count', 3)
        self.retry_delay = pydash.objects.get(properties, 'retry_delay', 1)

        self.redlock_client = Redlock([{"host": self.host, "port": self.port, "db": self.db}], retry_count=self.retry_count, retry_delay=self.retry_delay)

        connection_pool = ConnectionPool(host=self.host, port=self.port, decode_responses=True)
        self.connection = Redis(connection_pool=connection_pool)

    def __lock_tree(self, resource):
        # lock time in milliseconds
        # ops for locking/checking/updating/releasing resource tree should be done within 10 seconds
        return self.redlock_client.lock(f'LOCK:{resource}', 10000)

    # expiration in seconds
    def lock(self, resource, path, expiration):
        locked = False
        tree_lock = self.__lock_tree(resource)
        if tree_lock:
            try:
                keys = path.split(".")
                current_path = f'LOCK:{resource}'
                lockable = True
                for key in keys:
                    current_path += ":" + key
                    # check if node is a leaf
                    leaf = self.connection.keys(pattern=current_path)
                    if not pydash.is_empty(leaf):
                        lockable = False
                        break
                parent = self.connection.keys(pattern=f'{current_path}:*')
                if not pydash.is_empty(parent):
                    lockable = False
                if lockable:
                    self.connection.set(current_path, 1, ex=expiration)
                    locked = True
            finally:
                self.redlock_client.unlock(tree_lock)
        return locked

    def __get_arg_values(self, func, *args, **kwargs):
        signature = inspect.signature(func)
        bound_arguments = signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        arg_values = {}
        for param_name, param in signature.parameters.items():
            arg_values[param_name] = bound_arguments.arguments[param_name]
        return arg_values

    def with_json_lock(self, resource, expiration=60):
        def with_args(task_func):
            @functools.wraps(task_func)
            def wrapper(*args, **kwargs):
                try:
                    arg_values = self.__get_arg_values(task_func, *args, **kwargs)

                    while True:
                        locked = self.lock(resource, f'{arg_values["namespace"]}:{arg_values["key"]}', expiration)
                        if locked:
                            task_func(*args, **kwargs)
                            self.unlock(resource, f'{arg_values["namespace"]}:{arg_values["key"]}')
                            break
                        time.sleep(1)
                except Exception as ex:
                    raise Exception(ex)

            return wrapper

        return with_args

    def unlock(self, resource, key):
        tree_lock = self.__lock_tree(resource)
        if tree_lock:
            try:
                self.connection.delete(f'LOCK:{resource}:{key.replace(".", ":")}')
            finally:
                self.redlock_client.unlock(tree_lock)
