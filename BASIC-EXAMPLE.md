# Basic Hello World Example 1

Let's try running a very basic example. In this example, a user agent emits some text and a counter agent simply listens to the user agent and returns the number of words in the text from the user agent.

Note:

- Before proceeding forward, we should let you know that you would rarely run agents through python scripts as below. It is more preferrable that you build docker images and deploy them either through the web interface or command-line interface.
- Prerequisites. Make sure to run `build_agent.sh` under `agents/user` and `agents/counter`, and then install the requirements.txt through `pip install -r src/requirements.txt` in both of these directories.

**Step 1)** User Agent enters some text a session is created

To input some text through the user agent, run:

```
$ cd agents/user
$ python src/user_agent.py --interactive --loglevel ERROR
Session: SESSION:953b015
Enter Text: Hello, world!
```

Please note down the session that the USER agent created (i.e. SESSION:953b015)

**Step 2)** Counter agent does the following:

- Picks up the stream created by the USER agent.
- Computes the length of the USER stream.
- outputs that into another stream in the session.
-

Run the following to execute the COUNTER agent with the session from Step 1:

```
$ cd agents/counter
$ python src/counter_agent.py --session SESSION:953b015 --loglevel ERROR
[...]
```

You can see the log output from the counter agent to see its output. You can also see the demo stream contents using RedisInsight or use Observer agent (see [Observer](agents/observer)).
</br>

# Basic Hello World Example 2

Now let's do a more sophisticted example would be where the agent doesn't do the heavy work itself (counting is hard!) but merely makes a call to a service over websockets. To run an example like that you first need to bring up a web service and then run the agent that talks to the service.

**Step 1)** Let's first build the service as a docker image:

```
$ cd services/websocket_counter
$ ./docker_build_service.sh
```

**Step 2)** Then deploy the service:

```
$ cd platform/scripts
$ ./deploy_service.sh --service websocket_counter --port_mapping 8001:8001 --image blue-service-websocket_counter:latest
```

**Step 3)** And lastly run the agent:

```
$ cd agents/websocket_counter
$ python src/websocket_counter_agent.py --session SESSION:953b015 --properties='{"counter.service":"ws://localhost:8001"}'
```

</br>
</br>
