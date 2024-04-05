# postgres agent

Postgres Agent essentially scans a stream for any valid SQL statements and executes the query against its database. To bring up a Postgress agent, you need to provide properties such as host name, port, database, etc. For example:
```
$ cd agents/postgres
# python src/postgres_agent.py --properties  '{"postgres.user":"postgres", "postgres.password":"example", "postgres.database":"mydatabase", "postgres.host":"host.docker.internal"}' --session <SESSION>
```
Note that any properties with the prefix `postgres.` will be passed on to Postgress service, everything else is used by the agent itself for data processing and preparation.

For the Postgress agent you would also need to start a webservice to execute queries on Postgres . To start the service :
```
$ cd agents/postgres
$ docker compose up 
```

The postgress database itself is part of the blue platform, and it runs when you bring up the platform services (as noted above in infrastructure)