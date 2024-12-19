# neo4j agent
NEO4J Agent essentially scans a stream for any neo4j/CYPHER query statements and executes the query against its database. To bring up a NEO4J agent, you need to provide properties such as host name, etc. For example:
```
$ cd agents/neo4j
# python src/neo4j_agent.py --properties  '{"neo4j.user":"neo4j", "neo4j.password":"neo4j", "neo4j.host":"bolt://host.docker.internal"}' --session <SESSION>
```
Note that any properties with the prefix `neo4j.` will be passed on to NEO4J service, everything else is used by the agent itself for data processing and preparation.

For the NEO4J agent you would also need to start a webservice to execute queries on Postgres . To start the service :
```
$ cd agents/neo4j
$ docker compose up 
```

The neo4j database itself is part of the blue platform, and it runs when you bring up the platform services (as noted above in infrastructure)