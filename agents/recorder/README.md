# recorder 
Recorder Agent essentially consumes every JSON stream in a session to find matches and writes them to session memory for every agents consumtion. `records` property is an array of records which consists of `variable`, `query`, and `single`, where the recorder agent executes JSONPATH query in `query` and assigns it to `variable` in the session. When a variable assignment is made it is announced in the recorder's stream.
```
$ cd agents/recorder
# python src/recorder.py --properties '{"records":[{"variale":<name>,"query":<jsonpath_query>},...]}' --session <SESSION>
```
