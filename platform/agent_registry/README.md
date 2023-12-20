# agent registry

Agent registry is a repository of agents that captures metadata about agents, including name, description, properties, input and output parameters, and image (docker) at a minimum. Agent registry defines a scope of agents that can be put to work on specific deployments. As such in a deployment there could be many agent registries where different set of agents can be used for different use cases. To facilitate this agent registry has a `name` that can be coupled with a user session to limit the agents. 

It is also expected that agent registry can be utilized by a planner agent to find suitable agents. To facilitate that agent registry supports parameteric (embeddings) search as well as keyword based search. 

## build

To build agent registry:
```
$ cd platform/agent_registry
$  ./docker_build_agentregistry.sh 
```

### run

To run agent registry, as a prerequisite you need to have the platform up and running:
```
$ cd platform
$ ./start.sh
```

Then, you can run agent registry either as a python function:
```
$ cd platform/agent_registry
$ python src/agent_registry.py --list
```

Or as a docker container:
```
$ docker run -e parameters='--search title' --network="host" blue-agentregistry
```

Note above name of the agent registry is not provided as such `default` is used as the name

### properties

Agent registry has a number of properties that can be configured when a registry is created:

* host: host of the Redis database backend, default 'localhost'
* port: port address of the Redis database backend, default 6379
* embeddings_model: name of the embeddings model from huggingface, sentence transformer library, default `paraphrase-MiniLM-L6-v2`

### command line parameters

```
--name: type=str, default='default', help='name of the agent registry'
--properties', type=str, help='properties in json format'
--loglevel', default="INFO", type=str, help='log level'
--add', type=str, default=None, help='json array of agents to be add to the registry  (e.g. [{'name': 'TitleRecommender', 'description': 'Recommends next title given a title', 'image': 'blue-agent-simple_graph:latest'}]'
--remove', type=str, default=None, help='json array of agents names to be removed'
--search', type=str, default=None, help='search registry with keywords'
--type', type=str, default=None, help='search registry limited to agent metadata type [description, input, output]'
--page', type=int, default=0, help='search result page, default 0'
--page_size', type=int, default=5, help='search result page size, default 5'
--list', type=bool, default=False, help='list agents in the registry'
--approximate', type=bool, default=False, help='use approximate (embeddings) search'
--hybrid', type=bool, default=False, help='use hybrid (keyword and approximate) search'
```

#### add agents
```
$ python src/agent_registry.py --add "`cat data/sample_agents.json`"
```

#### search agents
Approximate agent search using only agent descriptions:
```
$ python src/agent_registry.py --search "`cat data/query2.txt`" --approximate --type description
```

Approximate agent input parameter search using only input parameters:
```
$ python src/agent_registry.py --search resume --approximate --type input
```