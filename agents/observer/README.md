# observer 
Observer Agent essentially consumes every stream in a session and outputs the contents into a readable format that can be used for demo and debugging purposes. To bring up an Observer agent, all you need is to pass the session to observe. For example:
```
$ cd agents/observer
# python src/observer.py  --session <SESSION>
```