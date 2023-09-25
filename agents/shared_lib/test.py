from inspect import signature

class A():
    def __init__(self, name, processor=None, properties={}):
        self.name = name
        self.properties = properties
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs, properties=self.properties)
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(*args, **kwargs, properties=self.properties)
    def default_processor(self, a, b, properties=None, worker=None):
        print('default')
        print(self)
        print(worker)
        print(properties)
        print(a)
        print(b)
    def run(self):
        b = B(processor=self.processor)
        print(b.processor)
        print(signature(b.processor))
        b.processor(3,5)

class B():
    def __init__(self, processor=None):
        # self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

def processor(a,b, properties=None, worker=None):
    print('custom')
    print(properties)
    print(worker)
    print(a)
    print(b)
    
print('---')
a = A('test', properties={'a':'123'})
a.run()
print('---')
a = A('test', processor=processor, properties={'a':'123'})
a.run()




