
# hello world example

Let's try running a very basic example. In this example, a user agent emits some text and a counter agent simply listens to the user agent and returns the number of words in the text from the user agent.

Note: Before proceeding forward, we should let you know that you would rarely run agents through python scripts as below. It is more preferrable that you build docker images and deploy them either through the web interface or command-line interface. 

Note: Prerequisites. Make sure to run `build_agent.sh` under `agents/user` and `agents/counter`, and then install the requirements.txt through `pip install -r src/requirements.txt` in both of these directories.

Now we can go back to the `hello world` example...


To input some text through the user agent, run:
```
$ cd agents/user
$ python src/user_agent.py --interactive --loglevel ERROR
Session: SESSION:953b015
Enter Text: Hello, world!
```

Then copy the session the USER agent created (i.e. SESSION:953b015)  so that another agent can participate in the same session:

```
$ cd agents/counter
$ python src/counter_agent.py --session SESSION:953b015 --loglevel ERROR
[...]
```

In the above example, the user enters some text and another agents listens to the sesssion the user agent works in, when the user agent creates a stream and enter text, the counter agent above picks up the stream and computes the length of the user stream and outputs that into another stream in the session. You can see the log output from the counter agent to see its output. You can also see the demo stream contents using RedisInsight or use Observer agent (see [Observer](agents/observer)).

Now let's do a more sophisticted 'hello world!'

A more sophisticated example would be where the agent doesn't do the heavy work itself (counting is hard!) but merely makes a call to a service over websockets. To run an example like that you first need to bring up a web service and then run the agent that talks to the service. Let's first build the service as a docker image:

```
$ cd services/websocket_counter
$ ./docker_build_service.sh
```

Then deploy the service:
```
$ cd platform/scripts
$ ./deploy_service.sh --service websocket_counter --port_mapping 8001:8001 --image blue-service-websocket_counter:latest
```

And lastly run the agent:
```
$ cd agents/websocket_counter
$ python src/websocket_counter_agent.py --session SESSION:953b015 --properties='{"counter.service":"ws://localhost:8001"}'
```


</br>
</br>

---

# development

To learn more about developing agents yourself please go to [agents](agents) for more details.


</br>
</br>

---

# demos

There are more demos in the [demos](demos) folder. Please try them on your own following the documentation in the respective folders.

</br>
</br>
