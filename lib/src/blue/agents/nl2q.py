###### Parsers, Formats, Utils
import logging
import json


###### Blue
from blue.agents.openai import OpenAIAgent
from blue.stream import Message
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
- When interpreting the "question" use additional context provided, if available. Ignore information in the context if the question overrides it.
- The SQL query should be compatible with the schema of the datasource.
- The SQL query should be compatible with the syntax of the corresponding database's protocol. Examples of protocol include "mysql" and "postgres".
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
    "nl2q_source": None,
    "nl2q_source_database": None,
    "nl2q_discovery": False,
    "nl2q_discovery_similarity_threshold": 0.2,
    "nl2q_discovery_source_protocols": ["postgres","mysql"],
    "nl2q_execute": True,
    "nl2q_case_insensitive": True,
    "nl2q_valid_query_prefixes": ["SELECT"],
    "nl2q_force_query_prefixes": ["SELECT"],
    "nl2q_additional_requirements": [],
    "nl2q_context": [],
    "nl2q_output_filters": ["all"],
    "nl2q_output_max_results": None,
    "output_transformations": [
        {
            "transformation": "replace",
            "from": "```",
            "to": ""
        },
        {
            "transformation": "replace",
            "from": "json",
            "to": ""
        }
    ],
    "output_strip": True,
    "output_cast": "json",
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


    def _initialize_properties(self):
        super()._initialize_properties()

        # intialize defatult properties
        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    def _start(self):
        super()._start()

        # initialize registry
        self._init_registry()

        # initalize sources, schema
        self._init_source()

        self._init_schemas()


    def _init_registry(self):
        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix, properties=self.properties)

    def _init_source(self):

        # initialiaze, optional settings
        self.schemas = {}
        self.selected_source = None
        self.selected_source_protocol = None
        self.selected_database = None
        self.selected_collection = None

        # select source, if set
        if "nl2q_source" in self.properties and self.properties["nl2q_source"]:
            self.selected_source = self.properties["nl2q_source"]

            source_properties = self.registry.get_source_properties(self.selected_source)

            if source_properties:
                if 'connection' in source_properties:
                    connection_properties = source_properties["connection"]

                    protocol = connection_properties["protocol"]
                    if protocol:
                        self.selected_source_protocol = protocol
                        
            # select database, if set
            self.selected_database = None
            if "nl2q_source_database" in self.properties and self.properties["nl2q_source_database"]:
                self.selected_database = self.properties['nl2q_source_database']

            # select collection, if set
            self.selected_collection = None
            if "nl2q_source_database_collection" in self.properties and self.properties["nl2q_source_database_collection"]:
                self.selected_collection = self.properties['nl2q_source_database_collection']

            # set protocol, if source specified
            source_properties = self.registry.get_source_properties(self.selected_source)
            self.selected_source_protocol = source_properties['connection']['protocol']

    def _init_schemas(self):

            # preset schema if any selected
            self._set_schemas(self.schemas, source=self.selected_source, database=self.selected_database, collection=self.selected_collection)
        
    def _set_schemas(self, schemas, source=None, database=None, collection=None):
        if source:

            source_properties = self.registry.get_source_properties(source)
            source_protocol = source_properties['connection']['protocol']

            # only allow source protocols that are allowed for discovery
            if "nl2q_discovery_source_protocols" in self.properties and self.properties["nl2q_discovery_source_protocols"]:
                if source_protocol not in self.properties["nl2q_discovery_source_protocols"]:
                    return

            if database:
                if collection:
                    entities = self.registry.get_source_database_collection_entities(source, database, collection)
                    if entities:
                        key = f'/{source}/{database}/{collection}'
                        schemas[key] = entities
                else:
                    # get collections
                    collections = self.registry.get_source_database_collections(source=source, database=database)

                    # set schemas for each collection
                    if collections is None:
                        collections = []
                    for collection in collections:
                        self._set_schemas(schemas, source=source, database=database, collection=collection['name'])
            else:
                # get databases
                databases = self.registry.get_source_databases(source=source)
                
                if databases is None:
                    database = []
                # set schemas for each database
                for database in databases:
                    self._set_schemas(schemas, source=source, database=database['name'])
        else:
            # get sources
            sources = self.registry.get_sources()

            if source is None:
                sources = []
            # set scheas for each source
            for source in sources:
                self._set_schemas(schemas, source=source['name'])

    def _parse_data_scope(self, scope):

        source = None
        database = None
        collection = None 

        if scope:
            sa = scope.split("/")
            if len(sa) > 1:
                source = sa[1]
                if source == '':
                    source = None
            if len(sa) > 2:
                database = sa[2]
                if database == '':
                    database = None
            if len(sa) > 3:
                collection = sa[3]
                if collection == '':
                    collection = None 

        return source, database, collection

    def _search_schemas(self, question, scope=None):
        schemas = {}

        if "nl2q_discovery_similarity_threshold" in self.properties and self.properties["nl2q_discovery_similarity_threshold"]:
            similarity_threshold = self.properties["nl2q_discovery_similarity_threshold"]
        else:
            similarity_threshold = 0.2

        # search matches below similarity threshold
        matches = []
        page = 0

        # progressively get more pages within similarity threshold
        while True:
            results = self.registry.search_records(question, scope=scope, approximate=True, page=page, page_size=5, page_limit=10) 
            
            if len(results) == 0:
                break
            for result in results:
                score = float(result['score'])
                if score < similarity_threshold:
                    matches.append(result)
                else:
                    break
            if score > similarity_threshold:
                break
            else:
                page = page + 1
            
        # process matches
        for match in matches:

            n = match["name"]
            t = match["type"]
            s = match["scope"]

            source, database, collection = self._parse_data_scope(s)
           
            if t == "source":
                source = n
            elif t == "database":
                database = n
            elif t == "collection":
                collection = n

            self._set_schemas(schemas, source=source, database=database, collection=collection)

        return schemas

    def _format_schema(self, schema):
        res = []
        for entity in schema:
            res.append({
                'table_name': entity['name'],
                'columns': ", ".join(list(entity['properties']['properties'].keys()))
            })
        return res

    def extract_input_params(self, input_data, properties=None):

        question = input_data

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        schemas = {}

        if "nl2q_discovery" in self.properties:
            if self.properties["nl2q_discovery"]:
                # set scope, if selected 
                scope = None
                if self.selected_source:
                    scope = ""
                    scope = scope +  "/" + self.selected_source
                    if self.selected_database:
                        scope = scope + "/" + self.selected_database
                        if self.selected_collection:
                            scope = scope + "/" + self.selected_collection
                    scope = scope + "*"
                # search registry to suggest schema
                schemas = self._search_schemas(question, scope=scope)
            else:
                # set schema from initialization
                schemas = self.schemas

        # source metadata
        sources = [{
            'source': key,
            'schema': self._format_schema(schema)
        } for key, schema in schemas.items()]

        sources = json.dumps(sources, indent=2)

        params = {
            'sources': sources,
            'question': question,
            'sensitivity': 'insensitive' if properties['nl2q_case_insensitive'] else 'sensitive',
            'force_query_prefixes': ', '.join(properties['nl2q_force_query_prefixes']),
            'protocol': self.selected_source_protocol if self.selected_source_protocol is not None else 'postgres',
            'additional_requirements': '\n- '.join(properties['nl2q_additional_requirements']),
            'context': '\n- '.join(properties['nl2q_context'])
        }

        return params

    def _apply_filter(self, output):
        output_filters = ['all']

        if 'nl2q_output_filters' in self.properties:
            output_filters = self.properties['nl2q_output_filters']

        question = output['question']
        source = output['source']
        query = output['query']
        result = output['result']
        error = output['error']

        # max results
        if "nl2q_output_max_results" in self.properties and self.properties['nl2q_output_max_results']:
            if isinstance(result, list):
                result = result[:self.properties['nl2q_output_max_results']]

        message = None
        if 'all' in output_filters:
            message = {
                'question': question,
                'source': source,
                'query': query,
                'result': result,
                'error': error
            }
            return message
            
        elif len(output_filters) == 1:
            if 'question' in output_filters:
                message = question
            if 'source' in output_filters:
                message = source
            if 'query' in output_filters:
                message = query
            if 'error' in output_filters:
                message = error
            if 'result' in output_filters:
                message = result
        else:
            message = {}
            if 'question' in output_filters:
                message['question'] = question
            if 'source' in output_filters:
                message['source'] = source
            if 'query' in output_filters:
                message['query'] = query
            if 'result' in output_filters:
                message['result'] = result
            if 'error' in output_filters:
                message['error'] = error
        
        return message

            
    def process_output(self, output_data, properties=None):

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        if type(output_data) == str:
            output_data = json.loads(output_data)

        question, key, query, result, error = None, None, None, None, None

        try:
            question = output_data['question']
            key = output_data['source']
            query = output_data['query']

            # validate query predicate
            if not any(query.upper().startswith(prefix.upper()) for prefix in properties['nl2q_valid_query_prefixes']):
                raise ValueError(f'Invalid query prefix: {query}')
            
            # extract source, database, collection
            source, database, collection = self._parse_data_scope(key)
            
            result = None

            # execute query, if configured
            if "nl2q_execute" in self.properties and self.properties['nl2q_execute']:
                 # connect
                source_connection = self.registry.connect_source(source)
            
                # execute
                logging.info("source: " + source)
                logging.info("database: " + database)
                logging.info("collection: " + collection)
                logging.info("executing query: " + query)
                result = source_connection.execute_query(query, database=database, collection=collection)
                logging.info(result)
               

        except Exception as e:
            error = str(e)

        # output
        output = {
            'question': question,
            'source': key,
            'query': query,
            'result': result,
            'error': error
        }
        logging.info(output)
        x = self._apply_filter(output)
        logging.info(str(x))
        return x
