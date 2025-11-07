###### Parsers, Formats, Utils
import logging
import json


###### Blue
from blue.agents.openai import OpenAIAgent
from blue.stream import Message
from blue.data.registry import DataRegistry


##########################
### OpenAIAgent.NL2SQLAgent
#
class NL2SQLAgent(OpenAIAgent):
    """An agent that translates natural language questions into SQL queries using an LLM.
    
    Properties (in addition to OpenAIAgent properties):
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `nl2q_source`    | `str`                 | `None`     | The data source name to use for schema and query execution. If None, discovery mode is used to suggest sources. |
    | `nl2q_source_database` | `str`            | `None`     | The database name within the source to use. If None, all databases are considered. |
    | `nl2q_discovery` | `bool`               | `False`    | Whether to use discovery mode to suggest schemas based on the question. |
    | `nl2q_discovery_similarity_threshold` | `float` | `0.2` | The similarity threshold for discovery mode (lower is more similar). |
    | `nl2q_case_insensitive` | `bool`        | `True`     | Whether to use case-insensitive matching for string comparisons. |
    | `nl2q_valid_query_prefixes` | `list of str` | `["SELECT"]` | List of valid SQL query prefixes. Queries not starting with these prefixes will be rejected. |
    | `nl2q_force_query_prefixes` | `list of str` | `["SELECT"]` | List of SQL query prefixes that the generated query must start with. |
    | `nl2q_additional_requirements` | `list of str` | `[]` | Additional requirements to include in the prompt. |
    | `nl2q_context`  | `list of str`      | `[]`       | Additional context to include in the prompt. |
    | `nl2q_output_filters` | `list of str` | `["all"]` | List of output fields to include in the final output. Options include "all", "question", "source", "query", "result", "error", "count". |
    | `nl2q_output_max_results` | `int`        | `None`     | Maximum number of results to return from the executed query. If None, all results are returned. |
    | `nl2q_fuzzy_match` | `bool`             | `True`     | Whether to use fuzzy matching for string comparisons in the generated SQL query. |

    Inputs:
    - DEFAULT: natural language input to transform into SQL

    Outputs:
    - DEFAULT: transformed SQL, tagged as `QUERY` and `SQL`

    """

    PROMPT = """
Your task is to translate a natural language question into a SQL query based on a list of provided data sources.
For each source you will be provided with a list of table schemas that specify the columns and their types. 
For enum fields, do not use LOWER(), ILIKE, or other string functions.
Compare enum fields using exact equality.

Here are the requirements:
- The output should be a JSON object with the following fields
  - "question": the original natural language question
  - "source": the name of the data source that the query will be executed on
  - "query": the SQL query that is translated from the natural language question
- When interpreting the "question" use additional context provided, if available. Ignore information in the context if the question overrides it.
- The SQL query should be compatible with the schema of the datasource.
- The SQL query should be compatible with the syntax of the corresponding database's protocol. Examples of protocol include "mysql", "postgres", and "sqlite".
- Always do case-${sensitivity} matching for string comparison.
- The query should starts with any of the following prefixes: ${force_query_prefixes}
- Output the JSON directly. Do not generate explanation or other additional output.
${additional_requirements}
${fuzzy_matching_block}

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

    PROPERTIES = {
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "output_path": "$.choices[0].message.content",
        "input_json": "[{\"role\":\"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": PROMPT,
        "openai.temperature": 0,
        "openai.max_tokens": 512,
        "nl2q_source": None,
        "nl2q_source_database": None,
        "nl2q_discovery": False,
        "nl2q_discovery_similarity_threshold": 0.2,
        "nl2q_discovery_source_protocols": ["postgres", "mysql", "sqlite"],
        "nl2q_execute": True,
        "nl2q_case_insensitive": True,
        "nl2q_valid_query_prefixes": ["SELECT"],
        "nl2q_force_query_prefixes": ["SELECT"],
        "nl2q_additional_requirements": [],
        "nl2q_context": [],
        "nl2q_output_filters": ["all"],
        "nl2q_output_max_results": None,
        "nl2q_fuzzy_match": True,
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2SQL"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # intialize defatult properties
        for key in NL2SQLAgent.PROPERTIES:
            self.properties[key] = NL2SQLAgent.PROPERTIES[key]

        if self.properties.get("nl2q_fuzzy_match"):
            self.properties[
                "fuzzy_matching_block"
            ] = """When comparing text fields, use fuzzy matching:
            - Use ILIKE '%value%' for partial string matching.
            - Avoid exact '=' unless comparing enum fields, codes, or IDs.
            """
        else:
            self.properties["fuzzy_matching_block"] = """Use exact matching for all fields unless otherwise specified."""

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the NL2SQL agent."""
        self.add_input("DEFAULT", description="natural language input to transform into SQL")

    def _initialize_outputs(self):
        """Initialize outputs for the NL2SQL agent, tagging output as QUERY and SQL."""
        self.add_output("DEFAULT", description="transformed SQL", tags=["QUERY", "SQL"])

    def _start(self):
        """Start the NL2SQL agent."""
        super()._start()

        # initialize registry
        self._init_registry()

        # initalize sources, schema
        self._init_source()

        self._init_schemas()

    def _init_registry(self):
        """Initialize the data registry."""
        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix, properties=self.properties)

    def _init_source(self):
        """Initialize the source for the NL2SQL agent."""
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
        """Initialize the schema for the NL2SQL agent."""
        # preset schema if any selected
        self._set_schemas(self.schemas, source=self.selected_source, database=self.selected_database, collection=self.selected_collection)

    def _set_schemas(self, schemas, source=None, database=None, collection=None, entity=None, relation=None, attribute=None):
        """Set schemas for the NL2SQL agent by querying the data registry.

        Parameters:
            schemas: The schemas dictionary to populate.
            source: The data source name.
            database: The database name.
            collection: The collection name.
            entity: The entity name.
            relation: The relation name.
            attribute: The attribute name.
        """
        if source:
            source_properties = self.registry.get_source_properties(source)
            source_protocol = source_properties['connection']['protocol']

            # only allow source protocols that are allowed for discovery
            if "nl2q_discovery_source_protocols" in self.properties and self.properties["nl2q_discovery_source_protocols"]:
                if source_protocol not in self.properties["nl2q_discovery_source_protocols"]:
                    return

            if database:
                if collection:
                    key = f'/source/{source}/database/{database}/collection/{collection}'
                    if key not in schemas:
                        schemas[key] = {'entities': [], 'relations': []}

                    if entity:
                        # look for entity in existing list
                        existing_entity = next((e for e in schemas[key]['entities'] if e['name'] == entity), None)

                        if existing_entity:
                            entity_dict = existing_entity
                        else:
                            entity_dict = self.registry.get_source_database_collection_entity(source, database, collection, entity)

                            # Initialize attributes list from contents if attribute=None
                            if attribute is None and 'contents' in entity_dict and 'attribute' in entity_dict['contents']:
                                entity_dict['attributes'] = list(entity_dict['contents']['attribute'].values())
                            else:
                                entity_dict['attributes'] = []

                            if 'contents' in entity_dict and 'attribute' in entity_dict['contents']:
                                del entity_dict['contents']['attribute']

                            schemas[key]['entities'].append(entity_dict)

                        # Add only the specified attribute
                        if attribute:
                            attribute_dict = self.registry.get_source_database_collection_entity_attribute(source, database, collection, entity, attribute)

                            if entity_dict:
                                if all(attr['name'] != attribute_dict['name'] for attr in entity_dict['attributes']):
                                    entity_dict['attributes'].append(attribute_dict)

                    if relation:
                        # look for relation in existing list
                        existing_relation = next((r for r in schemas[key]['relations'] if r['name'] == relation), None)

                        if existing_relation:
                            relation_dict = existing_relation
                        else:
                            relation_dict = self.registry.get_source_database_collection_relation(source, database, collection, relation)

                            if attribute is None and 'contents' in relation_dict and 'attribute' in relation_dict['contents']:
                                relation_dict['attributes'] = list(relation_dict['contents']['attribute'].values())
                            else:
                                relation_dict['attributes'] = []

                            if 'contents' in relation_dict and 'attribute' in relation_dict['contents']:
                                del relation_dict['contents']['attribute']

                            schemas[key]['relations'].append(relation_dict)

                        if attribute:
                            attribute_dict = self.registry.get_source_database_collection_relation_attribute(source, database, collection, relation, attribute)

                            if relation_dict:
                                if all(attr['name'] != attribute_dict['name'] for attr in relation_dict['attributes']):
                                    relation_dict['attributes'].append(attribute_dict)

                    if entity is None:
                        entities = self.registry.get_source_database_collection_entities(source, database, collection)
                        if entities:
                            normalized_entities = []
                            for e in entities:
                                if 'contents' in e and 'attribute' in e['contents']:
                                    e['attributes'] = list(e['contents']['attribute'].values())
                                    del e['contents']['attribute']
                                else:
                                    e['attributes'] = []
                                normalized_entities.append(e)
                            schemas[key]['entities'] = normalized_entities

                    if relation is None:
                        relations = self.registry.get_source_database_collection_relations(source, database, collection)
                        if relations:
                            normalized_relations = []
                            for r in relations:
                                if 'contents' in r and 'attribute' in r['contents']:
                                    r['attributes'] = list(r['contents']['attribute'].values())
                                    del r['contents']['attribute']
                                else:
                                    r['attributes'] = []
                                normalized_relations.append(r)
                            schemas[key]['relations'] = normalized_relations

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
                    databases = []

                # set schemas for each database
                for database in databases:
                    self._set_schemas(schemas, source=source, database=database['name'])

        else:
            # get sources
            sources = self.registry.get_sources()

            if sources is None:
                sources = []
                # set schemas for each source
            for source in sources:
                self._set_schemas(schemas, source=source['name'])

    def _parse_data_scope(self, scope):
        """Parse a data scope string into its components.

        Parameters:
            scope: The data scope string to parse.

        Returns:
            A tuple containing the parsed components (source, database, collection, entity, relation).
        """
        source = None
        database = None
        collection = None
        entity = None
        relation = None

        if scope:
            parts = scope.strip("/").split("/")

            it = iter(parts)

            for key in it:
                val = next(it, None)  # default to None if no more items
                if key == "source":
                    source = val or None
                elif key == "database":
                    database = val or None
                elif key == "collection":
                    collection = val or None
                elif key == "entity":
                    entity = val or None
                elif key == "relation":
                    relation = val or None

        return source, database, collection, entity, relation

    def _derive_thresholds(self, global_threshold, mode="hybrid", delta=0.10, factor=1.25, max_limit=1.0):
        """
        Derive local thresholds from the global threshold.

        Parameters:
            global_threshold: The global similarity threshold.
            mode: The mode of adjustment ("add", "mul", "hybrid").
            delta: The additive adjustment value (used in "add" and "hybrid" modes).
            factor: The multiplicative adjustment factor (used in "mul" and "hybrid" modes).
            max_limit: The maximum limit for the local threshold.

        Returns:
            A tuple containing the global and local thresholds.
        - similarity is distance-based: lower is better.
        - local_threshold >= global_threshold (i.e. more relaxed).
        """
        g = float(global_threshold)
        if mode == "add":
            local = min(g + delta, max_limit)
        elif mode == "mul":
            local = min(g * factor, max_limit)
        else:  # hybrid
            local = min(max(g * factor, g + delta), max_limit)

        # sanity: local must be >= global
        if local < g:
            local = g
        return g, local

    def _search_schemas(self, question, scope=None, discovery_depth_collection="some", discovery_depth_entity_relation="some"):
        """Search the data registry to suggest schemas based on the question and scope.

        Parameters:
            question: The natural language question to base the search on.
            scope: The scope to limit the search (e.g., specific source or database).
            discovery_depth_collection: The depth of discovery for collections ("all", "some", "none").
            discovery_depth_entity_relation: The depth of discovery for entities and relations ("all", "some", "none").

        Returns:
            A dictionary of suggested schemas.
        """
        schemas = {}

        if "nl2q_discovery_similarity_threshold" in self.properties and self.properties["nl2q_discovery_similarity_threshold"]:
            similarity_threshold = self.properties["nl2q_discovery_similarity_threshold"]
        else:
            similarity_threshold = 0.2

        similarity_threshold_global, similarity_threshold_local = self._derive_thresholds(similarity_threshold)

        # Step 1: Initial search to find matches
        matches = []
        page = 0

        while True:
            results = self.registry.search_records(question, scope=scope, approximate=True, page=page, page_size=5, page_limit=10)

            if not results:
                break

            page_has_match = False

            for result in results:
                score = float(result['score'])
                if score < similarity_threshold_global:
                    matches.append(result)
                    page_has_match = True

            if not page_has_match:
                break
            page += 1

        # Step 2: Upwards expansion - include parents for entity/relation/attribute
        expanded_matches = []
        seen = set()  # dedupe (type, name, scope)

        def _add_expanded(name, typ, sc):
            key = (typ, name, sc)
            if key not in seen:
                expanded_matches.append({"name": name, "type": typ, "scope": sc})
                seen.add(key)

        for match in matches:
            n = match["name"]
            t = match["type"]
            s = match["scope"]
            source, database, collection, entity, relation = self._parse_data_scope(s)

            # Expand upwards
            if t == "attribute":
                if entity and source is not None and database is not None and collection is not None:
                    parent_scope_entity = f'/source/{source}/database/{database}/collection/{collection}'
                    _add_expanded(entity, "entity", parent_scope_entity)
                if relation and source is not None and database is not None and collection is not None:
                    parent_scope_relation = f'/source/{source}/database/{database}/collection/{collection}'
                    _add_expanded(relation, "relation", parent_scope_relation)
                if collection and source is not None and database is not None:
                    parent_scope_collection = f'/source/{source}/database/{database}'
                    _add_expanded(collection, "collection", parent_scope_collection)
            elif t in ("entity", "relation"):
                if collection and source is not None and database is not None:
                    parent_scope_collection = f'/source/{source}/database/{database}'
                    _add_expanded(collection, "collection", parent_scope_collection)

            # Always include the original match
            _add_expanded(n, t, s)

        # Step 3: Downward processing (all / some)
        for match in expanded_matches:
            n = match["name"]
            t = match["type"]
            s = match["scope"]
            source, database, collection, entity, relation = self._parse_data_scope(s)

            if t == "collection":
                collection = n
                if discovery_depth_collection == "all":
                    self._set_schemas(schemas, source=source, database=database, collection=collection)

                elif discovery_depth_collection == "some":
                    child_scope = f'/source/{source}/database/{database}/collection/{collection}'
                    page = 0
                    while True:
                        results = self.registry.search_records(question, scope=child_scope, approximate=True, page=page, page_size=5, page_limit=10)
                        if not results:
                            break
                        page_has_match = False

                        for result in results:
                            score = float(result['score'])
                            result_type = result["type"]
                            if score < similarity_threshold_local:
                                page_has_match = True
                                if result_type == "entity":
                                    self._set_schemas(schemas, source=source, database=database, collection=collection, entity=result["name"])
                                elif result_type == "relation":
                                    self._set_schemas(schemas, source=source, database=database, collection=collection, relation=result["name"])
                        if not page_has_match:
                            break
                        page += 1

            elif t == "entity":
                entity = n
                if discovery_depth_entity_relation == "all":
                    self._set_schemas(schemas, source=source, database=database, collection=collection, entity=entity)
                elif discovery_depth_entity_relation == "some":
                    child_scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
                    page = 0
                    while True:
                        results = self.registry.search_records(question, scope=child_scope, approximate=True, page=page, page_size=5, page_limit=10)
                        if not results:
                            break
                        page_has_match = False
                        for result in results:
                            score = float(result['score'])
                            result_type = result["type"]

                            if score < similarity_threshold_local and result_type == "attribute":
                                self._set_schemas(schemas, source=source, database=database, collection=collection, entity=entity, attribute=result["name"])
                                page_has_match = True
                        if not page_has_match:
                            break
                        page += 1

            elif t == "relation":
                relation = n
                if discovery_depth_entity_relation == "all":
                    self._set_schemas(schemas, source=source, database=database, collection=collection, relation=relation)
                elif discovery_depth_entity_relation == "some":
                    child_scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
                    page = 0
                    while True:
                        results = self.registry.search_records(question, scope=child_scope, approximate=True, page=page, page_size=5, page_limit=10)
                        if not results:
                            break
                        page_has_match = False
                        for result in results:
                            score = float(result['score'])
                            result_type = result["type"]

                            if score < similarity_threshold_local and result_type == "attribute":
                                self._set_schemas(schemas, source=source, database=database, collection=collection, relation=relation, attribute=result["name"])
                                page_has_match = True
                        if not page_has_match:
                            break
                        page += 1

            elif t == "attribute":
                attribute = n
                if entity:
                    self._set_schemas(schemas, source=source, database=database, collection=collection, entity=entity, attribute=attribute)
                elif relation:
                    self._set_schemas(schemas, source=source, database=database, collection=collection, relation=relation, attribute=attribute)

            elif t == "database":
                # include the database
                database = n
                self._set_schemas(schemas, source=source, database=database)

        return schemas

    def _format_schema(self, schema):
        """Format the schema into a list of tables with their columns and types.

        Parameters:
            schema: The schema dictionary to format.

        Returns:
            A list of formatted tables with their columns and types.
        """
        res = []
        entities = schema['entities']

        for entity in entities:
            table_name = entity['name']
            attributes = entity['attributes']

            columns = []
            for col_info in attributes:
                col_entry = {"name": col_info.get("name"), "type": "unknown"}

                if isinstance(col_info, dict):
                    props = col_info.get("properties", {})
                    info = props.get("info", {})

                    col_entry["type"] = info.get("attr_type", col_info.get("type", "unknown"))

                    if "enum" in info:
                        col_entry["enum"] = info["enum"]

                    if "values" in info:
                        col_entry["values"] = info["values"]

                    if "stats" in props:
                        col_entry["stats"] = props["stats"]

                columns.append(col_entry)

            res.append({"table_name": table_name, "columns": columns})

        return res

    def extract_input_params(self, input_data, properties=None):
        """Extract input parameters from input data and properties for the API call.

        Parameters:
            input_data: The input data containing the natural language question.
            properties: Optional properties to override the agent's properties.

        Returns:
            A dictionary of input parameters for the API call."""
        question = input_data

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        schemas = {}

        if "nl2q_discovery" in self.properties:
            if self.properties["nl2q_discovery"]:
                # set scope, if selected
                scope = None

                if self.selected_source:
                    scope = "/source/" + self.selected_source
                    if self.selected_database:
                        scope += "/database/" + self.selected_database
                        if self.selected_collection:
                            scope += "/collection/" + self.selected_collection
                    scope += "*"
                # search registry to suggest schema
                schemas = self._search_schemas(question, scope=scope)
            else:
                # set schema from initialization
                schemas = self.schemas

        # source metadata
        sources = [{'source': key, 'schema': self._format_schema(schema)} for key, schema in schemas.items()]

        sources = json.dumps(sources, indent=2)

        params = {
            'sources': sources,
            'question': question,
            'sensitivity': 'insensitive' if properties['nl2q_case_insensitive'] else 'sensitive',
            'force_query_prefixes': ', '.join(properties['nl2q_force_query_prefixes']),
            'protocol': self.selected_source_protocol if self.selected_source_protocol is not None else 'postgres',
            'additional_requirements': '\n- '.join(properties['nl2q_additional_requirements']),
            'context': '\n- '.join(properties['nl2q_context']),
        }

        return params

    def _apply_filter(self, output):
        """Apply output filters to the output data.

        Parameters:
            output: The output data dictionary containing question, source, query, result, error, and count.

        Returns:
            The filtered output based on the specified output filters.
        """
        output_filters = ['all']

        if 'nl2q_output_filters' in self.properties:
            output_filters = self.properties['nl2q_output_filters']

        question = output['question']
        source = output['source']
        query = output['query']
        result = output['result']
        error = output['error']
        count = output['count']

        # max results
        if "nl2q_output_max_results" in self.properties and self.properties['nl2q_output_max_results']:
            if isinstance(result, list):
                result = result[: self.properties['nl2q_output_max_results']]

        message = None
        if 'all' in output_filters:
            message = {'question': question, 'source': source, 'query': query, 'result': result, 'error': error, 'count': count}
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
            if 'count' in output_filters:
                message = count
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
            if 'count' in output_filters:
                message['count'] = count

        return message

    def process_output(self, output_data, properties=None):
        """Process the output data from the API call and optionally execute the SQL query.

        Parameters:
            output_data: The output data from the API call, expected to be a JSON string or dictionary.
            properties: Optional properties to override the agent's properties.

        Returns:
            The processed output, which may include the executed query results.
        """
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        if type(output_data) == str:
            output_data = json.loads(output_data)

        question, key, query, result, error = None, None, None, None, None
        count = 0

        try:
            question = output_data['question']
            key = output_data['source']
            query = output_data['query']

            # validate query predicate
            if not any(query.upper().startswith(prefix.upper()) for prefix in properties['nl2q_valid_query_prefixes']):
                raise ValueError(f'Invalid query prefix: {query}')

            # extract source, database, collection, entity, relation
            source, database, collection, entity, relation = self._parse_data_scope(key)

            result = None

            # execute query, if configured
            if "nl2q_execute" in self.properties and self.properties['nl2q_execute']:
                # connect
                source_connection = self.registry.connect_source(source)

                # execute
                self.logger.info("source: " + source)
                self.logger.info("database: " + database)
                self.logger.info("collection: " + collection)
                self.logger.info("executing query: " + query)
                result = source_connection.execute_query(query, database=database, collection=collection)
                self.logger.info(result)

                count = len(result) if isinstance(result, list) else 0

        except Exception as e:
            error = str(e)

        # output
        output = {'question': question, 'source': key, 'query': query, 'result': result, 'error': error, 'count': count}
        self.logger.info(output)

        x = self._apply_filter(output)
        self.logger.info(str(x))
        return x


##########################
### NL2SQLAgent.Nl2CypherAgent
#
class Nl2CypherAgent(NL2SQLAgent):
    """Agent to convert natural language to Cypher queries for graph databases."""

    PROMPT = """
Your task is to translate a natural language question into a Cypher query based on a list of provided data sources.
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

    PROPERTIES = {
        "input_template": PROMPT,
        "nl2q_prompt": PROMPT,
        "nl2q_source": None,
        "nl2q_source_database": None,
        "nl2q_discovery": True,
        "nl2q_discovery_similarity_threshold": 0.2,
        "nl2q_discovery_source_protocols": ["bolt"],
        "nl2q_execute": True,
        "nl2q_case_insensitive": True,
        "nl2q_valid_query_prefixes": ["MATCH"],
        "nl2q_force_query_prefixes": ["MATCH"],
    }

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2CYPHER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # intialize defatult properties
        for key in Nl2CypherAgent.PROPERTIES:
            self.properties[key] = Nl2CypherAgent.PROPERTIES[key]

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the NL2Cypher agent."""
        self.add_input("DEFAULT", description="natural language input to transform into CYPHER")

    def _initialize_outputs(self):
        """Initialize outputs for the NL2Cypher agent, tagging output as QUERY and CYPHER."""
        self.add_output("DEFAULT", description="transformed CYPHER, optionally query results", tags=["QUERY", "CYPHER"])

    def _format_schema(self, schema):
        self.logger.info(f"Formatting schema: {schema}")
        return schema

    def _set_schemas(self, schemas, source=None, database=None, collection=None):
        """Set schemas for the NL2Cypher agent by querying the data registry.

        Parameters:
            schemas: The schemas dictionary to populate.
            source: The data source name.
            database: The database name.
            collection: The collection name.
        """
        if source and database and collection:
            entities = self.registry.get_source_database_collection_entities(source, database, collection)
            relations = self.registry.get_source_database_collection_relations(source, database, collection)
            if entities:
                key = f'/source/{source}/database/{database}/collection/{collection}'
                schemas[key] = {'entities': entities, 'relations': relations}
        else:
            super()._set_schemas(schemas, source, database, collection)


##########################
### NL2SQLAgent.NL2MongoQL
#
class NL2MongoQL(NL2SQLAgent):
    """Agent to convert natural language to MongoDB queries."""

    PROMPT = """
Your task is to translate a natural language question into a MongoDB MQL query based on a list of provided data sources.
For each source you will be provided with a list of table schemas that specify the columns and their types.

Here are the requirements:
- The output should be a JSON object with the following fields
  - "question": the original natural language question
  - "source": the name of the data source that the query will be executed on
  - "query": the MongoDB MQL query that is translated from the natural language question, must be a string instead of a JSON object.
- When interpreting the "question" use additional context provided, if available. Ignore information in the context if the question overrides it.
- The MongoDB MQL query should be compatible with the schema of the datasource.
- Always do case-${sensitivity} matching for string comparison.
- Output the JSON directly. Do not generate explanation or other additional output.
${additional_requirements}

Data sources:
```
${sources}
```

Context:
${context}

Question: ${question}
Output:
"""

    PROPERTIES = {
        "input_template": PROMPT,
        "nl2q_prompt": PROMPT,
        "nl2q_source": None,
        "nl2q_source_database": None,
        "nl2q_discovery": True,
        "nl2q_discovery_similarity_threshold": 0.2,
        "nl2q_discovery_source_protocols": ["mongodb"],
        "nl2q_execute": True,
        "nl2q_valid_query_prefixes": ["{"],
        "nl2q_force_query_prefixes": ["{"],
    }

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2MONGOQL"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # intialize defatult properties
        for key in NL2MongoQL.PROPERTIES:
            self.properties[key] = NL2MongoQL.PROPERTIES[key]

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize input parameters for the NL2MongoQL agent."""
        self.add_input("DEFAULT", description="natural language input to transform into MongoQL")

    def _initialize_outputs(self):
        """Initialize outputs for the NL2MongoQL agent, tagging output as QUERY and MONGOQL."""
        self.add_output("DEFAULT", description="transformed MongoQL, optionally query results", tags=["QUERY", "MONGOQL"])

    def _format_schema(self, schema):
        self.logger.info(f"Formatting schema: {schema}")
        return schema

    def _set_schemas(self, schemas, source=None, database=None, collection=None):
        """Set schemas for the NL2MongoQL agent by querying the data registry.

        Parameters:
            schemas: The schemas dictionary to populate.
            source: The data source name.
            database: The database name.
            collection: The collection name.
        """
        if source and database and collection:
            entities = self.registry.get_source_database_collection_entities(source, database, collection)
            relations = self.registry.get_source_database_collection_relations(source, database, collection)
            if entities:
                key = f'/source/{source}/database/{database}/collection/{collection}'
                schemas[key] = {'entities': entities, 'relations': relations}
        else:
            super()._set_schemas(schemas, source, database, collection)
