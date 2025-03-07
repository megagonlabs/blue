###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.agent import Agent, AgentFactory
from blue.agents.nl2q import NL2SQLAgent
from blue.session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

NL2CYPHER_PROMPT = """Your task is to translate a natural language question into a Cypher query based on a list of provided data sources.
For each source you will be provided with the graph schema that specifies the entities, relations and properties.

Here are the requirements:
- The output should be a JSON object with the following fields
  - "question": the original natural language question
  - "source": the name of the data source that the query will be executed on
  - "query": the Cypher query that is translated from the natural language question
- When interpreting the "question" use additional context provided, if available. Ignore information in the context if the question overrides it.
- The Cypher query should be compatible with the schema of the datasource.
- Always do case-${sensitivity} matching for string comparison.
- The query should starts with any of the following prefixes: ${force_query_prefixes}
- Output the JSON directly. Do not generate explanation or other additional output.
${additional_requirements}

Protocol:
```
${protocol}
```

Data sources:
```
${sources}
```

Context:
${context}

Question: ${question}
Output:
"""

agent_properties = {
    "input_template": NL2CYPHER_PROMPT,
    "nl2q_prompt": NL2CYPHER_PROMPT,
    "nl2q_source": None,
    "nl2q_source_database": None,
    "nl2q_discovery": True,
    "nl2q_discovery_similarity_threshold": 0.2,
    "nl2q_discovery_source_protocols": ["bolt"],
    "nl2q_execute": True,
    "nl2q_case_insensitive": True,
    "nl2q_valid_query_prefixes": ["MATCH"],
    "nl2q_force_query_prefixes": ["MATCH"]
}


class Nl2CypherAgent(NL2SQLAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2CYPHER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # intialize defatult properties
        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    def _format_schema(self, schema):
        logging.info(f"Formatting schema: {schema}")
        return schema

    def _set_schemas(self, schemas, source=None, database=None, collection=None):
        if source and database and collection:
            entities = self.registry.get_source_database_collection_entities(source, database, collection)
            relations = self.registry.get_source_database_collection_relations(source, database, collection)
            if entities:
                key = f'/{source}/{database}/{collection}'
                schemas[key] = {
                    'entities': entities,
                    'relations': relations
                }
        else:
            super()._set_schemas(schemas, source, database, collection)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="NL2CYPHER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    args = parser.parse_args()

    for i in range(10):
        print('qwer' * 100 + str(i))

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    if args.serve:
        platform = args.platform

        af = AgentFactory(_class=Nl2CypherAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = Nl2CypherAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = Nl2CypherAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
