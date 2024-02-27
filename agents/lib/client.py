from rpc import RPCClient

server = RPCClient('test_client')

server.connect()

print(server.add(5, 6))
print(server.sub(5, 6))

server.disconnect()

 class A:
    def __init__(self, name, properties={}):
        print(name)
        print(properties)
        self.start()
    def start(self):
        self.rpc = RPCServer("A", properties={})
        self.rpc.register(self.attend_session)
        self.rpc.run()
    def _get_instance(self, *args, **kwargs):
        return type(self)(*args, **kwargs)
    def attend_session(self, *args, **kwargs):
        agent = self._get_instance(*args, **kwargs) 