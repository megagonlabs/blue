###### Parsers, Formats, Utils
import logging
import json


###### Blue
from blue.agent import Agent
from blue.agents.openai import OpenAIAgent
from blue.data.registry import DataRegistry

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")



NL2SQL_PROMPT = """Your task is to translate a natural language question into a SQL query based on a list of provided data sources.
For each source you will be provided with a list of table schemas that specify the columns and their types.

Here are the requirements:
- The output should be a JSON object with the following fields
  - "question": the original natural language question
  - "source": the name of the data source that the query will be executed on
  - "query": the SQL query that is translated from the natural language question
- The SQL query should be compatible with the schema of the datasource.
- The SQL query should be compatible with the syntax of the corresponding database's protocol. Examples of protocol include "mysql" and "postgres".
- Always do case-${sensitivity} matching for string comparison.
- The query should starts with any of the following prefixes: ${force_query_prefixes}
- Output the JSON directly. Do not generate explanation or other additional output.

Protocol:
```
${protocol}
```

Data sources:
```
${sources}
```
Question: ${question}
Output:
"""

agent_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": NL2SQL_PROMPT,
    "openai.temperature": 0,
    "openai.max_tokens": 512,
    "nl2q.case_insensitive": True,
    "nl2q.protocols":["postgres","mysql"],
    "nl2q.valid_query_prefixes": ["SELECT"],
    "nl2q.force_query_prefixes": ["SELECT"],
    "listens": {
        "DEFAULT": {
            "includes": ["USER"],
            "excludes": []
        }
    }
}


##########################
### OpenAIAgent.NL2SQLAgent
#
class NL2SQLAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2SQL"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)
        self.schemas = {}
        self.selected_source = None
        self.selected_source_protocol = None
        # register all sources for Data Discovery only if source is not provided in the properties
        if "nl2q.source" in self.properties:
            self.selected_source = self.properties["nl2q.source"]
            self.selected_database = None
            if "nl2q.source.database" in self.properties:
                self.selected_database = self.properties['nl2q.source.database']

            source_properties = self.registry.get_source_properties(self.selected_source)
            self._add_sources_schema(self.selected_source, source_properties, database=self.selected_database)
            self.selected_source_protocol = source_properties['connection']['protocol']
        else:
            for source in self.registry.get_sources():
                source_properties = self.registry.get_source_properties(self.properties["nl2q.source"])
                self._add_sources_schema(source, source_properties)
        

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    def _add_sources_schema(self, source, properties, database=None):
        if ('connection' not in properties) or (properties['connection']['protocol'] not in self.properties["nl2q.protocols"]):
            return
        source_connection = self.registry.connect_source(source)
        try:
            databases = self.registry.get_source_databases(source)
            
            for db in databases:  # TODO: remove LLM data discovery
                if database:
                    if db['name'] != database:
                        continue
                try:
                    db = db['name']
                    #note: collection refers to table in mysql
                    if properties['connection']['protocol'] == 'mysql':
                        key = f'/{source}/{db}'
                        schema =  source_connection.fetch_database_collection_schema(db, None)
                        self.schemas[key] = schema
                    # Note: collection refers to schema in postgres (the level between database and table)
                    if properties['connection']['protocol'] == 'postgres':
                        for collection in self.registry.get_source_database_collections(source, db):
                            collection = collection['name']
                            assert all('/' not in s for s in [source, db, collection])
                            key = f'/{source}/{db}/{collection}'
                            schema =  source_connection.fetch_database_collection_schema(db, collection)
                            self.schemas[key] = schema
                except Exception as e:
                    logging.error(f'Error fetching schema for database: {db}, {str(e)}')
        except Exception as e:
            logging.error(f'Error fetching schema for source: {source}, {str(e)}')

    def _format_schema(self, schema):
        res = []
        for table_name, record in schema['entities'].items():
            res.append({
                'table_name': table_name,
                'columns': record['properties']
            })
        return res

    def extract_input_params(self, input_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        sources = [{
            'source': key,
            'schema': self._format_schema(schema)
        } for key, schema in self.schemas.items()]
        sources = json.dumps(sources, indent=2)
        # logging.info(f'<sources>{sources}</sources>')
        return {
            'sources': sources,
            'question': input_data,
            'sensitivity': 'insensitive' if properties['nl2q.case_insensitive'] else 'sensitive',
            'force_query_prefixes': ', '.join(properties['nl2q.force_query_prefixes']),
            'protocol': self.selected_source_protocol if self.selected_source_protocol is not None else 'postgres'
        }

    def process_output(self, output_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # logging.info(f'output_data: {output_data}')
        response = output_data.replace('```json', '').replace('```', '').strip()
        question, key, query, result, error = None, None, None, None, None
        try:
            response = json.loads(response)
            question = response['question']
            key = response['source']
            query = response['query']
            if not any(query.upper().startswith(prefix.upper()) for prefix in properties['nl2q.valid_query_prefixes']):
                raise ValueError(f'Invalid query prefix: {query}')
            _, source, database, collection = key.split('/')
            # connect
            source_connection = self.registry.connect_source(source)
            # execute query
            result = source_connection.execute_query(query, database=database, collection=collection)
        except Exception as e:
            error = str(e)
        return {
            'question': question,
            'source': key,
            'query': query,
            'result': result,
            'error': error
        }
