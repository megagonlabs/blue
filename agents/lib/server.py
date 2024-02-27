from rpc import RPCServer

def add(a, b):
    return a+b

def sub(a, b):
    return a-b

from rpc import RPCServer

server = RPCServer('test_server')

server.register(add)
server.register(sub)

server.run()
