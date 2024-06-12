# agent registry

Agent registry is a repository of agents that captures metadata about agents, including name, description, properties, input and output parameters, and image (docker) at a minimum. 

An example agent entry in the repository looks like this:
```
{
    "name": "Neo4J",
    "type": "agent",
    "scope": "/",
    "description": "Execute graph database queries against neo4j graph database",
    "properties": {
        "image": "blue-agent-neo4j:latest",
        "neo4j.user": "$NEO4J_USER",
        "neo4j.password": "$NEO4J_PWD",
        "neo4j.host": "$NEO4J_HOST"
    },
    "contents": {
        "query": {
            "name": "query",
            "type": "input",
            "scope": "/Neo4J",
            "description": "neo4j cypher query",
            "properties": {},
            "contents": {}
        },
        "result": {
            "name": "result",
            "type": "output",
            "scope": "/Neo4J",
            "description": "query results from executing the input query in JSON",
            "properties": {},
            "contents": {}
        }
    }
}
```

Agent registry defines the set of agents that can be put to utilized on specific deployments. When deployed each deployment (platform) is paired with a specific agent registry. Each agent registry has a `name` that is used in configuring a platform. 

Agent registry can be utilized by a planner agent to find suitable agents. To facilitate that agent registry supports parameteric (embeddings) search as well as keyword based search. 

## build

To build agent registry:
```
$ cd platform/agent_registry
$  ./docker_build_agentregistry.sh 
```

### run

To run agent registry, as a prerequisite you need to have the platform up and running.

Then, you can run agent registry either as a python function:
```
$ cd platform/agent_registry
$ python src/agent_registry.py --list
```

Note in the above case the properties of the agent registry may have to be additional set (for example `db.host`) to allow connections to database to store registry entiries. Note above name of the agent registry is not provided as such `default` is used.

Agent registry is also available on the web interface. 


### properties

Agent registry has a number of properties that can be configured when a registry is created:

* `db.host`: host of the Redis database backend, default 'localhost'
* `db.port`: port address of the Redis database backend, default 6379
* `embeddings_model`: name of the embeddings model from huggingface, sentence transformer library, default `paraphrase-MiniLM-L6-v2`

### command line parameters

```
--name', type=str, default='AGENT_REGISTRY', help='name of the registry'
--id', type=str, default='default', help='id of the registry'
--sid', type=str, help='short id (sid) of the registry'
--cid', type=str, help='canonical id (cid) of the registry'
--prefix', type=str, help='prefix for the canonical id of the registry'
--suffix', type=str, help='suffix for the canonical id of the registry'
--properties', type=str, help='properties in json format'
--loglevel', default="INFO", type=str, help='log level'
--add', type=str, default=None, help='json array of agents to be add to the registry'
--update', type=str, default=None, help='json array of agents to be updated in the registry'
--remove', type=str, default=None, help='json array of agents names to be removed'
--search', type=str, default=None, help='search registry with keywords'
--type', type=str, default=None, help='search registry limited to agent metadata type [agent, input, output]'
--scope', type=str, default=None, help='limit to scope'
--page', type=int, default=0, help='search result page, default 0'
--page_size', type=int, default=5, help='search result page size, default 5'
--list', type=bool, default=False, help='list agents in the registry'
--approximate', type=bool, default=False, help='use approximate (embeddings) search'
--hybrid', type=bool, default=False, help='use hybrid (keyword and approximate) search'
```
    
#### add agents

```
$ python src/agent_registry.py --add "`cat data/sample_agents.json`" --prefix PLATFORM:default
```

#### search agents

Approximate agent search using only agent metadata:
```
$ python src/agent_registry.py --search "`cat data/query2.txt`" --approximate --type agent
```

Approximate agent input parameter search using only input parameters:
```
$ python src/agent_registry.py --search resume --approximate --type input
```
